"""线索采集服务：用数据源拉线索并写入公司表。"""

from sqlalchemy.orm import Session

from app.datasources.base import DataSource
from app.models import Campaign, Company
from app.repositories.company_repo import CompanyRepository


class LeadService:
    def __init__(self, session: Session):
        self._session = session
        self._repo = CompanyRepository(session)

    def import_from(self, campaign: Campaign, source: DataSource) -> list[Company]:
        """从数据源拉取线索，写入 companies 表，返回新建的公司列表。"""
        created: list[Company] = []
        for raw in source.fetch():
            company = Company(
                campaign_id=campaign.id,
                name=raw.name,
                website=raw.website,
                country=raw.country,
                industry=raw.industry,
                description=raw.description,
                source=raw.source,
            )
            self._repo.add(company)
            created.append(company)
        self._session.commit()
        return created
