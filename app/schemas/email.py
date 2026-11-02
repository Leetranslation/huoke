from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EmailCreate(BaseModel):
    contact_id: int


class EmailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_id: int
    contact_id: Optional[int]
    subject: str
    body: str
    variant: str
    status: str
    created_at: datetime
    sent_at: Optional[datetime] = None
    company_name: str = ""
    contact_email: str = ""
    open_count: int = 0
    click_count: int = 0
    last_event_at: Optional[datetime] = None


class EventCreate(BaseModel):
    event_type: str


class EmailUpdate(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
