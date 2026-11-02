from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CampaignCreate(BaseModel):
    name: str
    product_name: str = ""
    website: str = ""
    target_market: list[str] = []
    keywords: list[str] = []


class CampaignOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    product_name: str
    website: str
    target_market: list[str] = []
    keywords: list[str] = []
    dna: dict = {}
    status: str
    created_at: datetime
