from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ExperienceBase(BaseModel):
    company: str
    location: str
    role: str
    start_date: datetime
    end_date: Optional[datetime] = None
    file_id: Optional[str] = None
    description: Optional[str] = None


class UpdateExperience(BaseModel):
    company: Optional[str] = None
    location: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    file_id: Optional[str] = None
    description: Optional[str] = None