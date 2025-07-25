from pydantic import BaseModel, Field
from typing import Optional


class TestimonialBase(BaseModel):   
    name: str
    title: str
    rating: int = Field(ge=1, le=5, default=1)
    message: str


class UpdateTestimonial(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    rating: Optional[int] = Field(ge=1, le=5, default=None)
    message: Optional[str] = None
    is_published: Optional[bool] = None
    position: Optional[int] = None
