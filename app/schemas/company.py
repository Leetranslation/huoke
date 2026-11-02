from pydantic import BaseModel, ConfigDict


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    campaign_id: int
    name: str
    website: str
    country: str
    industry: str
    description: str
    identity: str
    identity_reason: str
    source: str
    profile: dict
    match_score: float
