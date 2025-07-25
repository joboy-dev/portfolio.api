from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class CertificationBase(BaseModel):
    name: str
    issuer: str
    issue_date: Optional[datetime] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    issuer_file_id: Optional[str] = None


class UpdateCertification(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[datetime] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    issuer_file_id: Optional[str] = None
    position: Optional[int] = None
