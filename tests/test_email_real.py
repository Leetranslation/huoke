"""M4 真实调用验证：对 1 家公司做画像 + 生成开发信，人工检查质量。"""

import asyncio
import uuid
from pathlib import Path

from app.agent.email_writer import EmailWriter
from app.agent.llm import LLMClient
from app.agent.profiler import Profiler
from app.core.database import SessionLocal
from app.datasources.csv_source import CsvDataSource
from app.models import Campaign, Company, Contact, User
from app.services.email_service import EmailService
from app.services.lead_service import LeadService


async def main() -> None:
    llm = LLMClient()
    db = SessionLocal()
    try:
        user = User(email=f"m4r-{uuid.uuid4().hex[:8]}@example.com", password_hash="x")
        db.add(user)
        db.flush()
        camp = Campaign(user_id=user.id, name="m4 real", product_name="LED light")
        db.add(camp)
        db.flush()
        LeadService(db).import_from(camp, CsvDataSource(Path("data/sample_companies.csv")))

        company = db.query(Company).filter(Company.campaign_id == camp.id).first()

        profile = await Profiler(llm).profile(
            company.name, company.website, company.country, company.industry, camp.product_name
        )
        company.profile = {
            "industry": profile.industry,
            "demand_signals": profile.demand_signals,
            "match_reason": profile.match_reason,
        }
        company.match_score = profile.match_score
        db.flush()

        contact = Contact(
            company_id=company.id, name="John", title="Purchasing Manager", email="john@acme.com"
        )
        db.add(contact)
        db.flush()

        email = await EmailService(db, EmailWriter(llm)).generate(
            company, contact, camp.product_name
        )

        print("=" * 50)
        print("公司:", company.name, "| 匹配分:", company.match_score)
        print("主题:", email.subject)
        print("正文:")
        print(email.body)
        print("=" * 50)
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
