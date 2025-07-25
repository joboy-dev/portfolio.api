from pydantic import BaseModel
from typing import List, Optional


class ServiceBase(BaseModel):
    name: str
    description: str
    file_id: Optional[str] = None
    skills: Optional[List[str]] = None


class UpdateService(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    file_id: Optional[str] = None
    skills: Optional[List[str]] = None
