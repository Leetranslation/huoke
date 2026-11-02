"""邮件相关路由。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.agent.email_writer import EmailWriter
from app.api.deps import get_email_sender, get_email_writer
from app.core.database import get_db
from app.models import Campaign, Company, Contact, Email, EmailEvent
from app.schemas import EmailCreate, EmailOut, EmailUpdate, EventCreate
from app.senders.base import EmailSender
from app.services.email_service import EmailService
from app.services.send_service import SendService

router = APIRouter(tags=["emails"])


@router.post("/companies/{company_id}/emails", response_model=EmailOut)
async def generate_email(
    company_id: int,
    payload: EmailCreate,
    db: Session = Depends(get_db),
    writer: EmailWriter = Depends(get_email_writer),
):
    company = db.get(Company, company_id)
    if company is None:
        raise HTTPException(404, "company not found")
    contact = db.get(Contact, payload.contact_id)
    if contact is None:
        raise HTTPException(404, "contact not found")
    campaign = db.get(Campaign, company.campaign_id)
    return await EmailService(db, writer).generate(
        company, contact, campaign.product_name
    )


@router.get("/emails", response_model=list[EmailOut])
def list_emails(db: Session = Depends(get_db)):
    """邮件列表：带公司名、收件人、打开/点击次数（追踪统计）。"""
    rows = (
        db.query(Email, Company.name, Contact.email)
        .outerjoin(Company, Company.id == Email.company_id)
        .outerjoin(Contact, Contact.id == Email.contact_id)
        .order_by(Email.id.desc())
        .all()
    )

    # 聚合事件：打开次数 / 点击次数 / 最后事件时间
    stats_rows = (
        db.query(
            EmailEvent.email_id,
            func.sum(case((EmailEvent.event_type == "open", 1), else_=0)).label("opens"),
            func.sum(case((EmailEvent.event_type == "click", 1), else_=0)).label(
                "clicks"
            ),
            func.max(EmailEvent.occurred_at).label("last_at"),
        )
        .group_by(EmailEvent.email_id)
        .all()
    )
    stats = {
        r.email_id: (int(r.opens or 0), int(r.clicks or 0), r.last_at)
        for r in stats_rows
    }

    result: list[EmailOut] = []
    for email, company_name, contact_email in rows:
        opens, clicks, last_at = stats.get(email.id, (0, 0, None))
        item = EmailOut.model_validate(email)
        item.company_name = company_name or ""
        item.contact_email = contact_email or ""
        item.open_count = opens
        item.click_count = clicks
        item.last_event_at = last_at
        result.append(item)
    return result


@router.post("/emails/{email_id}/send")
def send_email(
    email_id: int,
    db: Session = Depends(get_db),
    sender: EmailSender = Depends(get_email_sender),
):
    email = db.get(Email, email_id)
    if email is None:
        raise HTTPException(404, "email not found")
    result = SendService(db, sender).send(email)
    return {"ok": result.ok, "message": result.message}


@router.patch("/emails/{email_id}")
def update_email(
    email_id: int,
    payload: EmailUpdate,
    db: Session = Depends(get_db),
):
    """编辑草稿（只有 draft 状态可编辑）。"""
    email = db.get(Email, email_id)
    if email is None:
        raise HTTPException(404, "email not found")
    if email.status != "draft":
        raise HTTPException(400, "只有草稿可以编辑")
    if payload.subject is not None:
        email.subject = payload.subject
    if payload.body is not None:
        email.body = payload.body
    db.commit()
    return {"ok": True, "status": email.status}


@router.post("/emails/{email_id}/events")
def record_event(
    email_id: int,
    payload: EventCreate,
    db: Session = Depends(get_db),
    sender: EmailSender = Depends(get_email_sender),
):
    email = db.get(Email, email_id)
    if email is None:
        raise HTTPException(404, "email not found")
    event = SendService(db, sender).record_event(email, payload.event_type)
    return {"event_type": event.event_type}


@router.post("/emails/{email_id}/submit")
def submit_email(email_id: int, db: Session = Depends(get_db)):
    email = db.get(Email, email_id)
    if email is None:
        raise HTTPException(404, "email not found")
    try:
        EmailService(db).submit(email)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return {"status": email.status}


@router.post("/emails/{email_id}/approve")
def approve_email(email_id: int, db: Session = Depends(get_db)):
    email = db.get(Email, email_id)
    if email is None:
        raise HTTPException(404, "email not found")
    try:
        EmailService(db).approve(email)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return {"status": email.status}


@router.post("/emails/{email_id}/reject")
def reject_email(email_id: int, db: Session = Depends(get_db)):
    email = db.get(Email, email_id)
    if email is None:
        raise HTTPException(404, "email not found")
    try:
        EmailService(db).reject(email)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return {"status": email.status}
