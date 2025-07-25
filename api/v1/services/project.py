from sqlalchemy.orm import Session

from api.utils.loggers import create_logger
from api.v1.models.project import Project
from api.v1.schemas import project as project_schemas


logger = create_logger(__name__)

class ProjectService:    
    pass