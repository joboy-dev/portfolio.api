from fastapi import UploadFile
from pydantic import BaseModel
from typing import Optional, List

from api.utils.form_factory import as_form_factory

class ProfileBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    title: str
    phone_number: Optional[str] = None
    phone_country_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    address: Optional[str] = None
    short_bio: Optional[str] = None
    about: Optional[str] = None
    interests: Optional[List[str]] = None
    hobbies: Optional[List[str]] = None
    resume_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    youtube_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    whatsapp_url: Optional[str] = None
    website_url: Optional[str] = None
    file: UploadFile

class UpdateProfile(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    phone_number: Optional[str] = None
    phone_country_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    address: Optional[str] = None
    short_bio: Optional[str] = None
    about: Optional[str] = None
    interests: Optional[List[str]] = None
    hobbies: Optional[List[str]] = None
    resume_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    youtube_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    whatsapp_url: Optional[str] = None
    website_url: Optional[str] = None
    file: Optional[UploadFile] = None
    
UpdateProfile.as_form = as_form_factory(UpdateProfile)
ProfileBase.as_form = as_form_factory(ProfileBase)
