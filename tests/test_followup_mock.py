"""M6 自动跟进 mock 测试：状态机基于生命周期 + 发送天数决策。"""

import asyncio
import json
import uuid
from pathlib import Path

from app.agent.graph import SEND, STOP, WAIT
from app.core.database import SessionLocal
from app.datasources.csv_source import CsvDataSource
from app.models import Campaign, Company, Contact, User
from app.models.enums import ContactStatus
from app.services.followup_service import FollowUpService
from app.services.lead_service import LeadService


class FakeLLM:
    async def chat(self, messages, **kwargs):
        return json.dumps({"intent": "positive"})


async def main() -> None:
    db = SessionLocal()
    try:
        user = User(email=f"m6-{uuid.uuid4().hex[:8]}@example.com", password_hash="x")
        db.add(user)
        db.flush()
        camp = Campaign(user_id=user.id, name="m6 test", product_name="LED light")
        db.add(camp)
        db.flush()
        LeadService(db).import_from(camp, CsvDataSource(Path("data/sample_companies.csv")))
        company = db.query(Company).filter(Company.campaign_id == camp.id).first()
        contact = Contact(
            company_id=company.id, name="John", title="Buyer", email="buyer@acme.com"
        )
        db.add(contact)
        db.flush()

        service = FollowUpService(db, FakeLLM(), follow_up_interval_days=4)

        contact.status = ContactStatus.PENDING
        assert service.decide(contact, 0) == SEND
        print("待触达(step0) ->", service.decide(contact, 0))

        contact.status = ContactStatus.QUALIFIED
        assert service.decide(contact, 0) == SEND
        print("已确认(step0) ->", service.decide(contact, 0))

        contact.status = ContactStatus.CONTACTED
        assert service.decide(contact, 1, days_since_last=0) == WAIT
        print("跟进中(step1, 0天) ->", service.decide(contact, 1, days_since_last=0))

        assert service.decide(contact, 1, days_since_last=5) == SEND
        print("跟进中(step1, 5天) ->", service.decide(contact, 1, days_since_last=5))

        contact.status = ContactStatus.REPLIED
        assert service.decide(contact, 2) == STOP
        print("已回复(step2) ->", service.decide(contact, 2))

        contact.status = ContactStatus.CONTACTED
        assert service.decide(contact, 5, days_since_last=10) == STOP
        print("跟进中(step5 达上限) ->", service.decide(contact, 5, days_since_last=10))

        contact.status = ContactStatus.UNSUBSCRIBED
        assert service.decide(contact, 1) == STOP
        print("退订 ->", service.decide(contact, 1))

        intent = await service.classify_reply("We are interested, please send catalog")
        print("回复意图:", intent)
        assert intent == "positive"

        print("FOLLOWUP MOCK TEST PASSED")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
