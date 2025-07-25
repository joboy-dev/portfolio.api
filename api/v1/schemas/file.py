from typing import List, Optional
from fastapi import UploadFile
from pydantic import BaseModel, field_validator
from api.utils.form_factory import as_form_factory

# @as_form
class FileBase(BaseModel):
    
    file: UploadFile
    file_name: Optional[str] = None
    model_id: Optional[str] = None
    model_name: str
    url: Optional[str] = None
    description: Optional[str] = None
    label: Optional[str] = None
    
    @field_validator( "model_name", "label", mode="before")
    @classmethod
    def strip_and_lower(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().lower() if isinstance(v, str) else v
    

# @as_form
class UpdateFile(BaseModel):
    
    # file: Optional[UploadFile]
    file_name: Optional[str] = None
    description: Optional[str] = None
    label: Optional[str] = None
    position: Optional[int] = None
    
    @field_validator("label", mode="before")
    @classmethod
    def strip_and_lower(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().lower() if isinstance(v, str) else v
    

class BulkUploadFile(BaseModel):
    files: List[UploadFile]
    model_id: Optional[str] = None
    model_name: str


FileBase.as_form = as_form_factory(FileBase)
UpdateFile.as_form = as_form_factory(UpdateFile)
BulkUploadFile.as_form = as_form_factory(BulkUploadFile)