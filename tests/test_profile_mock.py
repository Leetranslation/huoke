"""M3 画像匹配 mock 测试：验证「LLM 给维度分 + 后端加权算总分」。"""

import asyncio
import json
import uuid
from pathlib import Path

from app.agent.profiler import Profiler
from app.core.database import SessionLocal
from app.datasources.csv_source import CsvDataSource
from app.models import Campaign, Company, User
from app.services.lead_service import LeadService
from app.services.profile_service import ProfileService

DIMENSIONS = {
    "product_application": {"score": 90, "reason": "高度匹配"},
    "industry": {"score": 80, "reason": "同行业"},
    "buyer_type": {"score": 70, "reason": "买家类型吻合"},
    "target_market": {"score": 60, "reason": "目标市场部分吻合"},
    "procurement_fit": {"score": 50, "reason": "采购能力一般"},
    "demand_signal": {"score": 40, "reason": "需求信号弱"},
}
# 期望加权分 = 90*0.30 + 80*0.20 + 70*0.15 + 60*0.10 + 50*0.10 + 40*0.15 = 70.5


class FakeLLM:
    """假 LLM：返回固定维度分，不调真实 API。"""

    async def chat(self, messages, **kwargs):
        return json.dumps(
            {
                "industry": "Lighting",
                "business_description": "A lighting products company",
                "size": "mid-market",
                "demand_signals": ["needs LED lighting"],
                "dimensions": DIMENSIONS,
                "match_reason": "主营照明，与产品高度匹配",
            }
        )


async def main() -> None:
    db = SessionLocal()
    try:
        user = User(email=f"m3-{uuid.uuid4().hex[:8]}@example.com", password_hash="x")
        db.add(user)
        db.flush()
        camp = Campaign(user_id=user.id, name="m3 test", product_name="LED light")
        db.add(camp)
        db.flush()
        LeadService(db).import_from(camp, CsvDataSource(Path("data/sample_companies.csv")))

        await ProfileService(db, Profiler(FakeLLM())).profile_campaign(camp)

        companies = db.query(Company).filter(Company.campaign_id == camp.id).all()
        c = companies[0]
        assert c.match_score == 70.5, c.match_score
        assert c.profile["dimensions"]["product_application"]["score"] == 90
        print("画像公司数:", len(companies))
        print("样例:", c.name, "| 加权总分 =", c.match_score)
        print("维度分:", {k: v["score"] for k, v in c.profile["dimensions"].items()})
        print("PROFILE WEIGHTED SCORE TEST PASSED")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
