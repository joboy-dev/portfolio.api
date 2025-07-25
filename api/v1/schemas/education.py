from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class EducationBase(BaseModel):
    school: str
    location: str
    degree: Optional[str] = None
    grade: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    file_id: Optional[str] = None
    description: Optional[str] = None


class UpdateEducation(BaseModel):
    school: Optional[str] = None
    location: Optional[str] = None
    degree: Optional[str] = None
    grade: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    file_id: Optional[str] = None
    description: Optional[str] = None