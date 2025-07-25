from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AwardBase(BaseModel):
    name: str
    issuer: str
    issue_date: Optional[datetime] = None
    file_id: Optional[str] = None


class UpdateAward(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[datetime] = None
    file_id: Optional[str] = None


