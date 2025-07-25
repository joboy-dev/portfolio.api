from typing import Optional
from pydantic import BaseModel, EmailStr
import datetime as dt

    
class UpdateUser(BaseModel):
    
    email: Optional[EmailStr] = None
    old_password: Optional[str] = None
    password: Optional[str] = None

    
class AccountReactivationRequest(BaseModel):
    
    email: EmailStr
