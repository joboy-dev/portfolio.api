from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class TagBase(BaseModel):
    
    name: str = Field(min_length=1, max_length=100)
    model_type: str = Field(min_length=1, max_length=100)
    
    @field_validator("name", "model_type", mode="before")
    @classmethod
    def strip_and_lower(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().lower() if isinstance(v, str) else v


class UpdateTag(BaseModel):

    name: Optional[str] = None
    model_type: Optional[str] = None
    
    @field_validator("name", "model_type", mode="before")
    @classmethod
    def strip_and_lower(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().lower() if isinstance(v, str) else v


class AttachOrDetatchTag(BaseModel):
    
    tag_ids: List[str]
    entity_id: str
    model_type: str
