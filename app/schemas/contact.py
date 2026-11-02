from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ContactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_id: int
    name: str
    title: str
    email: str
    status: str
    company_name: str = ""
    last_sent_at: Optional[datetime] = None
    open_count: int = 0
    click_count: int = 0
    last_reply_subject: str = ""
    last_reply_at: Optional[datetime] = None
