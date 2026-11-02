"""Europages 数据源测试：爬取公司 + 落库（只爬一次）。"""

import uuid

from app.core.database import SessionLocal
from app.datasources.europages_source import EuropagesDataSource
from app.models import Campaign, Company, User


def main() -> None:
    print("开始爬取 Europages（led lighting，最多 5 家）...", flush=True)
    source = EuropagesDataSource("led lighting", max_companies=5)
    companies = source.fetch()
    print(f"爬到公司数: {len(companies)}", flush=True)
    for c in companies:
        print(f" - {c.name} | {c.country} | {c.website}", flush=True)

    if not companies:
        print("未爬到数据")
        return

    db = SessionLocal()
    try:
        user = User(email=f"ep-{uuid.uuid4().hex[:8]}@example.com", password_hash="x")
        db.add(user)
        db.flush()
        camp = Campaign(user_id=user.id, name="europages test", product_name="LED light")
        db.add(camp)
        db.flush()
        for c in companies:
            db.add(
                Company(
                    campaign_id=camp.id,
                    name=c.name,
                    website=c.website,
                    country=c.country,
                    industry=c.industry,
                    source=c.source,
                )
            )
        db.commit()
        print(f"落库成功: {len(companies)} 家公司", flush=True)
        print("EUROPAGES CRAWL TEST PASSED")
    finally:
        db.close()


if __name__ == "__main__":
    main()
