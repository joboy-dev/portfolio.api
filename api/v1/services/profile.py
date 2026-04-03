from sqlalchemy.orm import Session

from api.utils.loggers import create_logger
from api.v1.models.profile import Profile
from api.v1.models.project import Project
from api.v1.models.skill import Skill
from api.v1.schemas import profile as profile_schemas


logger = create_logger(__name__)

class ProfileService:
    
    @classmethod
    def load_properties(cls, db: Session, objs: list):
        _, _, project_count = Project.fetch_by_field(db, paginate=False)
        _, _, skill_count = Skill.fetch_by_field(db, paginate=False)
        
        for obj in objs:
            if isinstance(obj, Profile):
                obj._projects_count = project_count
                obj._skills_count = skill_count
