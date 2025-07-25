from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class MessageBase(BaseModel):
    name: str
    email: EmailStr
    phone_country_code: Optional[str] = None
    phone_number: Optional[str] = None
    message: str
    location: Optional[str] = None
    
    @field_validator('phone_country_code', mode='before')
    @classmethod
    def validate_phone_country_code(cls, v, values):
        if values.data.get('phone') and not v:
            raise ValueError("phone_country_code is required when phone is provided")
        return v

    @field_validator('phone_number', mode='before')
    @classmethod
    def validate_phone_number(cls, v, values):
        if values.data.get('phone_country_code') and not v:
            raise ValueError("phone_number is required when phone_country_code is provided")
        
        if v and not v.isdigit():
            raise ValueError("Phone numbers must contain only digits")
        return v
