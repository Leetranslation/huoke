"""M4 邮件生成 mock 测试：不调真实 LLM，验证生成与落库。"""

import asyncio
import json
import uuid
from pathlib import Path

from app.agent.email_writer import EmailWriter
from app.core.database import SessionLocal
from app.datasources.csv_source import CsvDataSource
from app.models import Campaign, Company, Contact, User
from app.services.email_service import EmailService
from app.services.lead_service import LeadService


class FakeLLM:
    """假 LLM：返回固定邮件 JSON。"""

    async def chat(self, messages, **kwargs):
        return json.dumps(
            {
                "subject": "Re: LED lighting for Acme",
                "body": "Dear John,\n\nWe noticed Acme's manufacturing facilities...\n\nBest regards",
            }
        )


async def main() -> None:
    db = SessionLocal()
    try:
        user = User(email=f"m4-{uuid.uuid4().hex[:8]}@example.com", password_hash="x")
        db.add(user)
        db.flush()
        camp = Campaign(user_id=user.id, name="m4 test", product_name="LED light")
        db.add(camp)
        db.flush()
        LeadService(db).import_from(camp, CsvDataSource(Path("data/sample_companies.csv")))
        company = db.query(Company).filter(Company.campaign_id == camp.id).first()

        contact = Contact(
            company_id=company.id, name="John", title="Buyer", email="buyer@acme.com"
        )
        db.add(contact)
        db.flush()

        email = await EmailService(db, EmailWriter(FakeLLM())).generate(
            company, contact, camp.product_name
        )

        assert email.subject and email.body
        print("生成邮件 subject:", email.subject)
        print("body 前 60 字:", email.body[:60])
        print("EMAIL GENERATE MOCK TEST PASSED")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
