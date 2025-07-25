from sqlalchemy.orm import Session

from api.utils.loggers import create_logger
from api.v1.models.skill import Skill
from api.v1.schemas import skill as skill_schemas


logger = create_logger(__name__)

class SkillService:    
    pass