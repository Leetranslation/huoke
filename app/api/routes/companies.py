"""公司详情路由。"""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agent.llm import LLMClient
from app.agent.profiler import Profiler
from app.agent.prompts import TRANSLATE_SYSTEM
from app.core.database import get_db
from app.models import Company
from app.schemas import CompanyOut

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyOut])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).order_by(Company.match_score.desc()).all()


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="company not found")
    return company


@router.get("/{company_id}/replies")
def list_replies(company_id: int, db: Session = Depends(get_db)):
    """该公司收到的所有客户回复（含正文），倒序。"""
    from app.models import Email, EmailEvent

    replies = (
        db.query(EmailEvent)
        .join(Email, Email.id == EmailEvent.email_id)
        .filter(Email.company_id == company_id, EmailEvent.event_type == "reply")
        .order_by(EmailEvent.id.desc())
        .all()
    )
    return [
        {
            "id": e.id,
            "from": (e.meta or {}).get("from", ""),
            "subject": (e.meta or {}).get("subject", ""),
            "body": (e.meta or {}).get("body", ""),
            "date": (e.meta or {}).get("date", ""),
        }
        for e in replies
    ]


@router.post("/{company_id}/translate")
async def translate_profile(company_id: int, db: Session = Depends(get_db)):
    """把画像的英文内容翻译成中文，缓存到 profile["_zh"]（只翻译一次）。"""
    company = db.get(Company, company_id)
    if company is None:
        raise HTTPException(404, "company not found")

    profile = company.profile or {}
    if profile.get("_zh"):
        return profile["_zh"]

    fields = {
        "industry": profile.get("industry", ""),
        "business_description": profile.get("business_description", ""),
        "demand_signals": profile.get("demand_signals", []),
        "match_reason": profile.get("match_reason", ""),
    }
    text = await LLMClient().chat(
        [
            {"role": "system", "content": TRANSLATE_SYSTEM},
            {"role": "user", "content": json.dumps(fields, ensure_ascii=False)},
        ]
    )
    zh = Profiler._parse(text)
    if not zh:
        raise HTTPException(500, "translation failed")

    profile["_zh"] = zh
    company.profile = profile
    db.commit()
    return zh
