"""画像匹配服务：批量对公司做画像 + 评分（异步并发）。"""

import asyncio
import logging

from sqlalchemy.orm import Session

from app.agent.profiler import Profiler
from app.models import Campaign, Company
from app.repositories.company_repo import CompanyRepository

logger = logging.getLogger(__name__)


class ProfileService:
    def __init__(self, session: Session, profiler: Profiler):
        self._session = session
        self._profiler = profiler
        self._repo = CompanyRepository(session)

    async def profile_campaign(
        self, campaign: Campaign, concurrency: int = 5
    ) -> list[Company]:
        """并发对「非同行、非无关」的公司画像（信号量控制并发数）。"""
        all_companies = self._repo.list_by_campaign(campaign.id)
        companies = [
            c for c in all_companies if c.identity not in ("competitor", "irrelevant")
        ]
        sem = asyncio.Semaphore(concurrency)

        async def one(company: Company) -> None:
            async with sem:
                try:
                    profile = await self._profiler.profile(
                        company.name,
                        company.website,
                        company.country,
                        company.industry,
                        campaign.product_name,
                        company.description,
                    )
                    company.profile = {
                        "name_zh": profile.name_zh,
                        "industry": profile.industry,
                        "business_description": profile.business_description,
                        "size": profile.size,
                        "demand_signals": profile.demand_signals,
                        "dimensions": profile.dimensions,
                        "match_reason": profile.match_reason,
                    }
                    company.match_score = profile.match_score
                except Exception as e:  # noqa: BLE001
                    logger.warning("画像失败 %s: %s", company.name, e)

        await asyncio.gather(*[one(c) for c in companies])
        self._session.commit()
        return all_companies
