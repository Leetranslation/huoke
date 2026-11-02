"""邮件生成服务：生成开发信 + 人工审核流转。"""

from sqlalchemy.orm import Session

from app.agent.email_writer import EmailWriter
from app.models import Company, Contact, Email
from app.models.enums import EmailStatus


class EmailService:
    def __init__(self, session: Session, writer: EmailWriter | None = None):
        self._session = session
        self._writer = writer

    async def generate(self, company: Company, contact: Contact, product: str) -> Email:
        """基于公司画像 + 决策人生成开发信（落库为草稿）。"""
        if self._writer is None:
            raise ValueError("生成邮件需要 EmailWriter")
        draft = await self._writer.write(
            product,
            company.name,
            company.profile or {},
            contact_name=contact.name,
            contact_title=contact.title,
        )
        email = Email(
            campaign_id=company.campaign_id,
            company_id=company.id,
            contact_id=contact.id,
            subject=draft.subject,
            body=draft.body,
        )
        self._session.add(email)
        self._session.commit()
        return email

    def submit(self, email: Email) -> Email:
        """提交审核：draft -> pending_approval。"""
        if email.status != EmailStatus.DRAFT:
            raise ValueError(f"只有草稿可提交审核（当前 {email.status}）")
        email.status = EmailStatus.PENDING_APPROVAL
        self._session.commit()
        return email

    def approve(self, email: Email) -> Email:
        """批准发送：pending_approval -> approved。"""
        if email.status != EmailStatus.PENDING_APPROVAL:
            raise ValueError(f"只有待审批邮件可批准（当前 {email.status}）")
        email.status = EmailStatus.APPROVED
        self._session.commit()
        return email

    def reject(self, email: Email) -> Email:
        """打回：pending_approval -> draft。"""
        if email.status != EmailStatus.PENDING_APPROVAL:
            raise ValueError(f"只有待审批邮件可打回（当前 {email.status}）")
        email.status = EmailStatus.DRAFT
        self._session.commit()
        return email
