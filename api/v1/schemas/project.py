from pydantic import BaseModel, HttpUrl
from typing import List, Optional

from api.v1.schemas.base import AdditionalInfoSchema


class ProjectBase(BaseModel):
    name: str
    tagline: Optional[str] = None
    description: Optional[str] = None
    tools: Optional[List[str]] = None
    domain: str
    project_type: str
    role: str
    client: Optional[str] = None
    github_link: Optional[HttpUrl] = None
    postman_link: Optional[HttpUrl] = None
    live_link: Optional[HttpUrl] = None
    google_drive_link: Optional[HttpUrl] = None
    figma_link: Optional[HttpUrl] = None
    features: Optional[List[str]] = None
    challenges_and_solutions: Optional[List[str]] = None
    results: Optional[List[str]] = None
    technical_details: Optional[List[AdditionalInfoSchema]] = None


class UpdateProject(BaseModel):
    name: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    tools: Optional[List[str]] = None
    features: Optional[List[str]] = None
    challenges_and_solutions: Optional[List[str]] = None
    results: Optional[List[str]] = None
    technical_details: Optional[List[AdditionalInfoSchema]] = None
    technical_details_keys_to_remove: Optional[List[str]] = None
    domain: Optional[str] = None
    project_type: Optional[str] = None
    role: Optional[str] = None
    client: Optional[str] = None
    github_link: Optional[HttpUrl] = None
    postman_link: Optional[HttpUrl] = None
    live_link: Optional[HttpUrl] = None
    google_drive_link: Optional[HttpUrl] = None
    figma_link: Optional[HttpUrl] = None
    position: Optional[int] = None
