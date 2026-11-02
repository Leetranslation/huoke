"""定时跟进任务：每天扫描联系人，需要跟进的生成跟进信草稿（待人工审批）。"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from app.agent.email_writer import EmailWriter
from app.agent.llm import LLMClient
from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Campaign, Company, Contact, Email, EmailEvent
from app.models.enums import ContactStatus, EmailStatus
from app.services.followup_service import FollowUpService

logger = logging.getLogger(__name__)

# 默认值兜底（真实取值见 settings.follow_up_*，可用环境变量覆盖）
FOLLOW_UP_INTERVAL_DAYS = 4
MAX_STEPS = 5


def _classify_intent(body: str) -> str:
    """同步版回复意图判断（Celery 任务里用，避免 asyncio.run 反复建 loop）。"""
    import httpx

    from app.agent.prompts import REPLY_INTENT_SYSTEM, build_intent_prompt

    if not body.strip():
        return "neutral"
    try:
        r = httpx.post(
            f"{settings.llm_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.llm_model,
                "messages": [
                    {"role": "system", "content": REPLY_INTENT_SYSTEM},
                    {"role": "user", "content": build_intent_prompt(body)},
                ],
                "temperature": 0.1,
            },
            timeout=40,
        )
        if r.status_code != 200:
            logger.warning("意图判断 HTTP %s: %s", r.status_code, r.text[:150])
            return "neutral"
        text = (r.json()["choices"][0]["message"]["content"] or "").strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text).get("intent", "neutral")
    except Exception as e:  # noqa: BLE001
        logger.warning("意图判断失败: %s", e)
        return "neutral"


@celery_app.task(name="app.tasks.followup.daily_scan")
def daily_scan() -> dict:
    """扫描所有「跟进中」联系人：到间隔就生成跟进信草稿。"""
    db = SessionLocal()
    created = 0
    scanned = 0
    try:
        now = datetime.now(timezone.utc)
        contacts = (
            db.query(Contact).filter(Contact.status == ContactStatus.CONTACTED).all()
        )
        scanned = len(contacts)
        service = FollowUpService(
            db,
            max_steps=settings.follow_up_max_steps,
            follow_up_interval_days=settings.follow_up_interval_days,
        )
        writer = EmailWriter(LLMClient())

        for contact in contacts:
            sent_count = (
                db.query(func.count(Email.id))
                .filter(
                    Email.contact_id == contact.id, Email.status == EmailStatus.SENT
                )
                .scalar()
                or 0
            )
            last_sent = (
                db.query(func.max(Email.sent_at))
                .filter(
                    Email.contact_id == contact.id, Email.status == EmailStatus.SENT
                )
                .scalar()
            )
            if last_sent is None:
                continue

            days = (now - last_sent).days
            action = service.decide(contact, sent_count, days)
            if action != "send":
                continue

            # 最近 7 天内已有草稿才跳过（避免旧草稿永久阻塞跟进）
            recent_cut = now - timedelta(days=7)
            pending = (
                db.query(Email)
                .filter(
                    Email.contact_id == contact.id,
                    Email.status == EmailStatus.DRAFT,
                    Email.created_at >= recent_cut,
                )
                .first()
            )
            if pending is not None:
                continue

            company = db.get(Company, contact.company_id)
            campaign = db.get(Campaign, company.campaign_id) if company else None
            if company is None or campaign is None:
                continue

            last_subject = (
                db.query(Email.subject)
                .filter(
                    Email.contact_id == contact.id, Email.status == EmailStatus.SENT
                )
                .order_by(Email.id.desc())
                .limit(1)
                .scalar()
                or ""
            )

            try:
                draft = asyncio.run(
                    writer.write_followup(
                        campaign.product_name,
                        company.name,
                        contact.name,
                        sent_count + 1,
                        last_subject,
                    )
                )
            except Exception as e:  # noqa: BLE001
                logger.warning("跟进信生成失败 contact=%s: %s", contact.id, e)
                continue

            if not draft.subject or not draft.body:
                continue

            email = Email(
                campaign_id=campaign.id,
                company_id=company.id,
                contact_id=contact.id,
                subject=draft.subject,
                body=draft.body,
                status=EmailStatus.DRAFT,
                model=settings.llm_model,
            )
            db.add(email)
            db.commit()
            created += 1
            logger.info("生成跟进信 contact=%s company=%s", contact.id, company.name)

        # 记录本次扫描时间（供前端展示）
        try:
            import redis as redis_lib

            client = redis_lib.from_url(settings.redis_url, decode_responses=True)
            client.set("yxagent:last_scan", datetime.now(timezone.utc).isoformat())
        except Exception:  # noqa: BLE001
            logger.warning("写入 last_scan 失败")

        return {"scanned": scanned, "created": created}
    finally:
        db.close()


@celery_app.task(name="app.tasks.followup.check_replies")
def check_replies() -> dict:
    """IMAP 收信：识别客户回复，更新状态并记录回复内容。"""
    from app.services.imap_service import fetch_replies

    import redis as redis_lib

    db = SessionLocal()
    matched = 0
    try:
        replies = fetch_replies(30)
        client = redis_lib.from_url(settings.redis_url, decode_responses=True)
        for r in replies:
            key = f"yxagent:reply:{r['uid']}"
            if client.get(key):
                continue  # 已处理过

            # 去掉 Re:/Fwd: 前缀，用于主题精确匹配原邮件
            raw_subj = re.sub(
                r"^\s*((re|fwd|fw|答复|回复|转发)\s*[:：]\s*)+",
                "",
                r["subject"] or "",
                flags=re.I,
            ).strip().lower()

            # 同邮箱可能有多个联系人（测试客户共用邮箱），先用主题匹配原邮件
            candidates = (
                db.query(Contact).filter(func.lower(Contact.email) == r["from"]).all()
            )
            contact = None
            last_email = None
            fallback = None  # (联系人, 最近一封已发送) 兜底
            for cand in candidates:
                sent = (
                    db.query(Email)
                    .filter(
                        Email.contact_id == cand.id,
                        Email.status == EmailStatus.SENT,
                    )
                    .order_by(Email.id.desc())
                    .all()
                )
                if not sent:
                    continue
                if fallback is None:
                    fallback = (cand, sent[0])
                if not raw_subj:
                    continue
                for e in sent:
                    es = re.sub(
                        r"^\s*((re|fwd|fw|答复|回复|转发)\s*[:：]\s*)+",
                        "",
                        e.subject or "",
                        flags=re.I,
                    ).strip().lower()
                    if es and es == raw_subj:
                        contact, last_email = cand, e
                        break
                if contact is not None:
                    break

            if contact is None and fallback is not None:
                contact, last_email = fallback

            if contact is None or last_email is None:
                continue

            # 用 LLM 判断回复意图：negative 直接退订，永不再发
            # 去掉引用的原始邮件，只判客户自己写的话
            clean = (
                r["body"]
                .split("---Original---")[0]
                .split("------------------ Original")[0]
                .strip()[:1200]
            )
            intent = _classify_intent(clean)

            new_status = (
                ContactStatus.UNSUBSCRIBED if intent == "negative" else ContactStatus.REPLIED
            )

            db.add(
                EmailEvent(
                    email_id=last_email.id,
                    event_type="reply",
                    meta={
                        "from": r["from"],
                        "subject": r["subject"],
                        "body": r["body"][:4000],
                        "date": r["date"],
                        "intent": intent,
                    },
                )
            )
            if contact.status != new_status:
                contact.status = new_status
            db.commit()
            client.set(key, "1")
            matched += 1
            logger.info(
                "识别到回复: %s -> company=%s intent=%s status=%s",
                r["from"],
                contact.company_id,
                intent,
                new_status,
            )

        return {"replies": len(replies), "matched": matched}
    finally:
        db.close()
