"""公司仓储。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Company
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, session: Session):
        super().__init__(session, Company)

    def list_by_campaign(self, campaign_id: int) -> list[Company]:
        stmt = (
            select(Company)
            .where(Company.campaign_id == campaign_id)
            .order_by(Company.match_score.desc())
        )
        return list(self._session.scalars(stmt).all())
