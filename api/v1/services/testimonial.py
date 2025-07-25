from sqlalchemy.orm import Session

from api.utils.loggers import create_logger
from api.v1.models.testimonial import Testimonial
from api.v1.schemas import testimonial as testimonial_schemas


logger = create_logger(__name__)

class TestimonialService:
    pass