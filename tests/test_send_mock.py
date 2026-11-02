"""M5 发送与追踪 mock 测试：发送 + 事件驱动生命周期（打开不改变状态）。"""

import uuid
from pathlib import Path

from app.core.database import SessionLocal
from app.datasources.csv_source import CsvDataSource
from app.models import Campaign, Company, Contact, Email, User
from app.models.enums import ContactStatus, EmailStatus, EventType
from app.senders.mock_sender import MockEmailSender
from app.services.lead_service import LeadService
from app.services.send_service import SendService


def main() -> None:
    db = SessionLocal()
    try:
        user = User(email=f"m5-{uuid.uuid4().hex[:8]}@example.com", password_hash="x")
        db.add(user)
        db.flush()
        camp = Campaign(user_id=user.id, name="m5 test", product_name="LED light")
        db.add(camp)
        db.flush()
        LeadService(db).import_from(camp, CsvDataSource(Path("data/sample_companies.csv")))
        company = db.query(Company).filter(Company.campaign_id == camp.id).first()
        contact = Contact(
            company_id=company.id, name="John", title="Buyer", email="buyer@acme.com"
        )
        db.add(contact)
        db.flush()
        email = Email(
            campaign_id=camp.id, company_id=company.id, contact_id=contact.id,
            subject="Hi", body="Hello",
        )
        db.add(email)
        db.flush()

        email.status = EmailStatus.APPROVED
        db.flush()

        service = SendService(db, MockEmailSender())

        result = service.send(email)
        assert result.ok
        assert email.status == EmailStatus.SENT
        db.refresh(contact)
        assert contact.status == ContactStatus.CONTACTED
        print("发送后 email.status:", email.status, "| contact.status:", contact.status)

        # 打开只记录事件，不改变生命周期（打开追踪不可靠）
        service.record_event(email, EventType.OPEN)
        db.refresh(contact)
        assert contact.status == ContactStatus.CONTACTED
        print("打开后 contact.status:", contact.status, "(应保持不变)")

        # 回复才改变生命周期
        service.record_event(email, EventType.REPLY)
        db.refresh(contact)
        assert contact.status == ContactStatus.REPLIED
        print("回复后 contact.status:", contact.status)

        print("SEND & TRACK MOCK TEST PASSED")
    finally:
        db.close()


if __name__ == "__main__":
    main()
