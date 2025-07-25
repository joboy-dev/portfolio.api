from typing import Any, List, Optional
from pydantic import BaseModel

from api.v1.models import *

class AdditionalInfoSchema(BaseModel):
    key: str
    value: Any
        
    
class DeleteMultiple(BaseModel):
    ids: List[str]


class PaginatedResponseBase(BaseModel):
    current_page: int
    size: int
    total: int
    pages: int
    previous_page: Optional[str] = None
    next_page: Optional[str] = None
