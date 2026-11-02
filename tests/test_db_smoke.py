"""M1 建表冒烟测试：验证 7 张表已建 + 完整链路 CRUD 正常。"""

import uuid

from sqlalchemy import text

from app.core.database import SessionLocal
from app.models import Campaign, Company, Contact, Email, User
from app.models.enums import ContactStatus


def main() -> None:
    db = SessionLocal()
    try:
        # 1. 验证 7 张表都在
        rows = db.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        ).scalars().all()
        tables = sorted(r for r in rows if not r.startswith("alembic"))
        print("表清单:", tables)
        assert tables == [
            "campaigns",
            "companies",
            "contacts",
            "email_events",
            "emails",
            "follow_up_steps",
            "users",
        ], tables

        # 2. 完整链路 CRUD：user -> campaign -> company -> contact -> email
        user = User(email=f"demo-{uuid.uuid4().hex[:8]}@example.com", password_hash="x")
        db.add(user)
        db.flush()

        camp = Campaign(user_id=user.id, name="demo campaign", product_name="LED light")
        db.add(camp)
        db.flush()

        company = Company(
            campaign_id=camp.id, name="Acme GmbH", country="DE", match_score=88.5
        )
        db.add(company)
        db.flush()

        contact = Contact(
            company_id=company.id, name="John", title="Buyer", email="buyer@acme.com"
        )
        db.add(contact)
        db.flush()

        email = Email(
            campaign_id=camp.id,
            company_id=company.id,
            contact_id=contact.id,
            subject="Hi John",
        )
        db.add(email)
        db.commit()

        # 3. 查询验证 + 状态默认值
        c = db.get(Contact, contact.id)
        assert c is not None and c.status == ContactStatus.PENDING
        print("链路 CRUD 通过，contact.status =", c.status)
        print("SMOKE TEST PASSED")
    finally:
        db.close()


if __name__ == "__main__":
    main()
