from typing import Any, Dict, List
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.ext.hybrid import hybrid_property

from api.core.base.base_model import BaseTableModel
from api.db.database import get_db_with_ctx_manager


class Profile(BaseTableModel):
    __tablename__ = 'profile'

    email = sa.Column(sa.String, nullable=False)
    first_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    title = sa.Column(sa.String, nullable=False)
    image_url = sa.Column(sa.String, nullable=False)
    phone_number = sa.Column(sa.String, nullable=True)
    phone_country_code = sa.Column(sa.String, nullable=True)
    city = sa.Column(sa.String, nullable=True)
    state = sa.Column(sa.String, nullable=True)
    country = sa.Column(sa.String, nullable=True)
    address = sa.Column(sa.Text, nullable=True)
    short_bio = sa.Column(sa.Text, nullable=True)
    about = sa.Column(sa.Text, nullable=True)
    interests = sa.Column(sa.JSON, nullable=True)
    hobbies = sa.Column(sa.JSON, nullable=True)
    resume_url = sa.Column(sa.String, nullable=True)
    github_url = sa.Column(sa.String, nullable=True)
    linkedin_url = sa.Column(sa.String, nullable=True)
    twitter_url = sa.Column(sa.String, nullable=True)
    facebook_url = sa.Column(sa.String, nullable=True)
    instagram_url = sa.Column(sa.String, nullable=True)
    youtube_url = sa.Column(sa.String, nullable=True)
    tiktok_url = sa.Column(sa.String, nullable=True)
    whatsapp_url = sa.Column(sa.String, nullable=True)
    website_url = sa.Column(sa.String, nullable=True)
    
    _projects_count = None
    _skills_count = None
    
    @hybrid_property
    def projects_count(self) -> int:
        return self._projects_count if self._projects_count is not None else 0
        
    @hybrid_property
    def skills_count(self) -> int:
        return self._skills_count if self._skills_count is not None else 0
    
    @hybrid_property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @classmethod
    def load_properties(cls, db: Session, objects: list):
        from api.v1.services.profile import ProfileService
        ProfileService.load_properties(db, objects)
    
    
    def to_dict(self, excludes: List[str]= []) -> Dict[str, Any]:
        return {
            "projects_count": self.projects_count,
            "skills_count": self.skills_count,
            "full_name": self.full_name,
            **super().to_dict(excludes)
        }
