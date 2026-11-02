"""跟进看板路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Company, Contact, Email, EmailEvent
from app.schemas import ContactOut

router = APIRouter(tags=["followup"])


@router.get("/contacts", response_model=list[ContactOut])
def list_contacts(db: Session = Depends(get_db)):
    """联系人列表（带公司名 + 最近发送时间 + 打开/点击次数）。"""
    rows = (
        db.query(Contact, Company.name)
        .outerjoin(Company, Company.id == Contact.company_id)
        .order_by(Contact.id.desc())
        .all()
    )

    # 聚合每个联系人的邮件追踪统计
    stats_rows = (
        db.query(
            Email.contact_id,
            func.max(Email.sent_at).label("last_sent_at"),
            func.sum(case((EmailEvent.event_type == "open", 1), else_=0)).label(
                "opens"
            ),
            func.sum(case((EmailEvent.event_type == "click", 1), else_=0)).label(
                "clicks"
            ),
        )
        .outerjoin(EmailEvent, EmailEvent.email_id == Email.id)
        .group_by(Email.contact_id)
        .all()
    )
    stats = {
        r.contact_id: (r.last_sent_at, int(r.opens or 0), int(r.clicks or 0))
        for r in stats_rows
    }

    # 聚合每个联系人的最近回复
    reply_rows = (
        db.query(
            Email.contact_id,
            func.max(EmailEvent.occurred_at).label("reply_at"),
        )
        .join(EmailEvent, EmailEvent.email_id == Email.id)
        .filter(EmailEvent.event_type == "reply")
        .group_by(Email.contact_id)
        .all()
    )
    reply_ids = {r.contact_id for r in reply_rows}

    result: list[ContactOut] = []
    for contact, company_name in rows:
        item = ContactOut.model_validate(contact)
        item.company_name = company_name or ""
        last_sent_at, opens, clicks = stats.get(contact.id, (None, 0, 0))
        item.last_sent_at = last_sent_at
        item.open_count = opens
        item.click_count = clicks
        if contact.id in reply_ids:
            reply = (
                db.query(EmailEvent)
                .join(Email, Email.id == EmailEvent.email_id)
                .filter(
                    Email.contact_id == contact.id,
                    EmailEvent.event_type == "reply",
                )
                .order_by(EmailEvent.id.desc())
                .first()
            )
            if reply is not None:
                item.last_reply_subject = (reply.meta or {}).get("subject", "")
                item.last_reply_at = reply.occurred_at
        result.append(item)
    return result


@router.post("/followup/run")
def run_followup_now():
    """手动触发跟进扫描（投递到 Celery，异步执行；等价于每天 9 点的定时任务）。"""
    from app.tasks.followup import daily_scan

    task = daily_scan.delay()
    return {"task_id": task.id, "status": "queued"}


@router.post("/followup/check-replies")
def check_replies_now():
    """手动触发收信检查（投递到 Celery，异步执行；等价于每 3 分钟的定时任务）。"""
    from app.tasks.followup import check_replies

    task = check_replies.delay()
    return {"task_id": task.id, "status": "queued"}


@router.get("/followup/last-scan")
def last_scan():
    """上次跟进扫描时间（Celery 任务执行后写入 Redis）。"""
    import redis

    from app.core.config import settings

    try:
        client = redis.from_url(settings.redis_url, decode_responses=True)
        value = client.get("yxagent:last_scan")
        return {"last_scan": value}
    except Exception:  # noqa: BLE001
        return {"last_scan": None}
