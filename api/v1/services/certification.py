from sqlalchemy.orm import Session

from api.utils.loggers import create_logger
from api.v1.models.certification import Certification
from api.v1.schemas import certification as certification_schemas


logger = create_logger(__name__)

class CertificationService:    
    pass