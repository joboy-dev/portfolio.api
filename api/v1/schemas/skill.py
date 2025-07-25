from pydantic import BaseModel, Field
from typing import Optional


class SkillBase(BaseModel):
    name: str
    proficiency: int = Field(le=100)
    file_id: Optional[str] = None 


class UpdateSkill(BaseModel):
    name: Optional[str] = None
    proficiency: Optional[int] = Field(default=None, le=100)
    file_id: Optional[str] = None 
    position: Optional[int] = None 
