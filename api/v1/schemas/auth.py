from typing import Optional
from pydantic import BaseModel, EmailStr


class CreateUser(BaseModel):
    
    email: EmailStr
    password: Optional[str] = None
    is_superuser: Optional[bool] = False
    

class LoginSchema(BaseModel):
    
    email: EmailStr
    password: str
    

class MagicLoginRequest(BaseModel):
    
    email: EmailStr
    
    
class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    password: str

    
class GoogleAuth(BaseModel):
    id_token: str
    