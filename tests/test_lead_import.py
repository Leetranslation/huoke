"""M2 线索采集冒烟测试：CSV 导入 -> companies 表有记录。"""

import uuid
from pathlib import Path

from app.core.database import SessionLocal
from app.datasources.csv_source import CsvDataSource
from app.models import Campaign, User
from app.services.lead_service import LeadService


def main() -> None:
    db = SessionLocal()
    try:
        user = User(email=f"lead-{uuid.uuid4().hex[:8]}@example.com", password_hash="x")
        db.add(user)
        db.flush()
        camp = Campaign(user_id=user.id, name="lead test", product_name="LED light")
        db.add(camp)
        db.flush()

        source = CsvDataSource(Path("data/sample_companies.csv"))
        companies = LeadService(db).import_from(camp, source)

        print("导入公司数:", len(companies))
        assert len(companies) > 0
        print("样例:", companies[0].name, "|", companies[0].country, "|", companies[0].industry)
        print("LEAD IMPORT PASSED")
    finally:
        db.close()


if __name__ == "__main__":
    main()
