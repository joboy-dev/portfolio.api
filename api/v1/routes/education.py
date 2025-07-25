from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils import paginator, helpers
from api.utils.responses import success_response
from api.utils.settings import settings
from api.v1.models.user import User
from api.v1.models.education import Education
from api.v1.services.auth import AuthService
from api.v1.services.education import EducationService
from api.v1.schemas import education as education_schemas
from api.utils.loggers import create_logger


education_router = APIRouter(prefix='/educations', tags=['Education'])
logger = create_logger(__name__)

@education_router.post("", status_code=201, response_model=success_response)
async def create_education(
    payload: education_schemas.EducationBase,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to create a new education"""

    education = Education.create(
        db=db,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'Education with id {education.id} created')

    return success_response(
        message=f"Education created successfully",
        status_code=201,
        data=education.to_dict()
    )


@education_router.get("", status_code=200)
async def get_educations(
    school: str = None,
    page: int = 1,
    per_page: int = 10,
    sort_by: str = 'start_date',
    order: str = 'desc',
    db: Session=Depends(get_db), 
):
    """Endpoint to get all educations"""

    query, educations, count = Education.fetch_by_field(
        db, 
        sort_by=sort_by,
        order=order.lower(),
        page=page,
        per_page=per_page,
        search_fields={'school': school},
    )
    
    return paginator.build_paginated_response(
        items=[education.to_dict() for education in educations],
        endpoint='/educations',
        page=page,
        size=per_page,
        total=count,
    )


@education_router.get("/{id}", status_code=200, response_model=success_response)
async def get_education_by_id(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to get a education by ID or unique_id in case ID fails."""

    education = Education.fetch_by_id(db, id)
    
    return success_response(
        message=f"Fetched education successfully",
        status_code=200,
        data=education.to_dict()
    )


@education_router.patch("/{id}", status_code=200, response_model=success_response)
async def update_education(
    id: str,
    payload: education_schemas.UpdateEducation,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to update a education"""

    education = Education.update(
        db=db,
        id=id,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'Education with id {education.id} updated')

    return success_response(
        message=f"Education updated successfully",
        status_code=200,
        data=education.to_dict()
    )


@education_router.delete("/{id}", status_code=200, response_model=success_response)
async def delete_education(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to delete a education"""

    Education.soft_delete(db, id)

    return success_response(
        message=f"Deleted successfully",
        status_code=200
    )

