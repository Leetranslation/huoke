"""审核流程与停止规则测试：draft→pending→approved→send + 三类拦截。"""

import uuid
from pathlib import Path

from app.core.database import SessionLocal
from app.datasources.csv_source import CsvDataSource
from app.models import Campaign, Company, Contact, Email, User
from app.models.enums import ContactStatus, EmailStatus
from app.senders.mock_sender import MockEmailSender
from app.services.email_service import EmailService
from app.services.lead_service import LeadService
from app.services.send_service import SendService


def main() -> None:
    db = SessionLocal()
    try:
        user = User(email=f"rv-{uuid.uuid4().hex[:8]}@example.com", password_hash="x")
        db.add(user)
        db.flush()
        camp = Campaign(user_id=user.id, name="review test", product_name="LED light")
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

        svc = EmailService(db)
        sender = SendService(db, MockEmailSender())

        # 1. 草稿未批准 → 禁止发送
        r = sender.send(email)
        assert not r.ok
        print("草稿发送被拦截:", r.message)

        # 2. 提交审核
        svc.submit(email)
        assert email.status == EmailStatus.PENDING_APPROVAL
        print("提交审核 ->", email.status)

        # 3. 待审批未批准 → 仍禁止发送
        r = sender.send(email)
        assert not r.ok
        print("待审批发送被拦截:", r.message)

        # 4. 批准
        svc.approve(email)
        assert email.status == EmailStatus.APPROVED
        print("批准 ->", email.status)

        # 5. 批准后发送成功
        r = sender.send(email)
        assert r.ok
        assert email.status == EmailStatus.SENT
        print("批准后发送 ->", email.status, "| contact:", contact.status)

        # 6. 重复发送 → 拦截
        r = sender.send(email)
        assert not r.ok
        print("重复发送被拦截:", r.message)

        # 7. 客户终止态 → 拦截
        contact.status = ContactStatus.UNSUBSCRIBED
        db.commit()
        email2 = Email(
            campaign_id=camp.id, company_id=company.id, contact_id=contact.id,
            subject="Hi2", body="Hello2", status=EmailStatus.APPROVED,
        )
        db.add(email2)
        db.flush()
        r = sender.send(email2)
        assert not r.ok
        print("退订客户发送被拦截:", r.message)

        print("REVIEW & STOP RULES TEST PASSED")
    finally:
        db.close()


if __name__ == "__main__":
    main()
