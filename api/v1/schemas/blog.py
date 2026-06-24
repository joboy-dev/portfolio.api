from fastapi import UploadFile
from pydantic import BaseModel
from typing import Optional

from api.utils.form_factory import as_form_factory


class BlogBase(BaseModel):
    title: str
    excerpt: Optional[str] = None
    content: str
    is_published: Optional[bool] = False


class UpdateBlog(BaseModel):
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    is_published: Optional[bool] = None
    position: Optional[int] = None


class BlogCoverImage(BaseModel):
    file: UploadFile


BlogCoverImage.as_form = as_form_factory(BlogCoverImage)
