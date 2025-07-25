from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils import paginator, helpers
from api.utils.responses import success_response
from api.utils.settings import settings
from api.v1.models.user import User
from api.v1.models.experience import Experience
from api.v1.services.auth import AuthService
from api.v1.services.experience import ExperienceService
from api.v1.schemas import experience as experience_schemas
from api.utils.loggers import create_logger


experience_router = APIRouter(prefix='/experiences', tags=['Experience'])
logger = create_logger(__name__)

@experience_router.post("", status_code=201, response_model=success_response)
async def create_experience(
    payload: experience_schemas.ExperienceBase,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to create a new experience"""

    experience = Experience.create(
        db=db,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'Experience with id {experience.id} created')

    return success_response(
        message=f"Experience created successfully",
        status_code=201,
        data=experience.to_dict()
    )


@experience_router.get("", status_code=200)
async def get_experiences(
    company: str = None,
    page: int = 1,
    per_page: int = 30,
    sort_by: str = 'start_date',
    order: str = 'desc',
    db: Session=Depends(get_db), 
):
    """Endpoint to get all experiences"""

    query, experiences, count = Experience.fetch_by_field(
        db, 
        sort_by=sort_by,
        order=order.lower(),
        page=page,
        per_page=per_page,
        search_fields={'company': company},
    )
    
    return paginator.build_paginated_response(
        items=[experience.to_dict() for experience in experiences],
        endpoint='/experiences',
        page=page,
        size=per_page,
        total=count,
    )


@experience_router.get("/{id}", status_code=200, response_model=success_response)
async def get_experience_by_id(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to get a experience by ID or unique_id in case ID fails."""

    experience = Experience.fetch_by_id(db, id)
    
    return success_response(
        message=f"Fetched experience successfully",
        status_code=200,
        data=experience.to_dict()
    )


@experience_router.patch("/{id}", status_code=200, response_model=success_response)
async def update_experience(
    id: str,
    payload: experience_schemas.UpdateExperience,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to update a experience"""

    experience = Experience.update(
        db=db,
        id=id,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'Experience with id {experience.id} updated')

    return success_response(
        message=f"Experience updated successfully",
        status_code=200,
        data=experience.to_dict()
    )


@experience_router.delete("/{id}", status_code=200, response_model=success_response)
async def delete_experience(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to delete a experience"""

    Experience.soft_delete(db, id)

    return success_response(
        message=f"Deleted successfully",
        status_code=200
    )

