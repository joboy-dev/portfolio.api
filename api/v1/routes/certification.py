from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import sqlalchemy as sa

from api.db.database import get_db
from api.utils import paginator, helpers
from api.utils.responses import success_response
from api.utils.settings import settings
from api.v1.models.user import User
from api.v1.models.certification import Certification
from api.v1.services.auth import AuthService
from api.v1.services.certification import CertificationService
from api.v1.schemas import certification as certification_schemas
from api.utils.loggers import create_logger


certification_router = APIRouter(prefix='/certifications', tags=['Certification'])
logger = create_logger(__name__)

@certification_router.post("", status_code=201, response_model=success_response)
async def create_certification(
    payload: certification_schemas.CertificationBase,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to create a new certification"""
    
    max_position = Certification.get_max_position(db)

    certification = Certification.create(
        db=db,
        position=max_position+1,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'Certification with id {certification.id} created')

    return success_response(
        message=f"Certification created successfully",
        status_code=201,
        data=certification.to_dict()
    )


@certification_router.get("", status_code=200)
async def get_certifications(
    name: str = None,
    page: int = 1,
    per_page: int = 10,
    sort_by: str = 'position',
    order: str = 'asc',
    db: Session=Depends(get_db), 
):
    """Endpoint to get all certifications"""

    query, certifications, count = Certification.fetch_by_field(
        db, 
        sort_by=sort_by,
        order=order.lower(),
        page=page,
        per_page=per_page,
        search_fields={'name': name},
    )
    
    return paginator.build_paginated_response(
        items=[certification.to_dict() for certification in certifications],
        endpoint='/certifications',
        page=page,
        size=per_page,
        total=count,
    )


@certification_router.get("/{id}", status_code=200, response_model=success_response)
async def get_certification_by_id(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to get a certification by ID or unique_id in case ID fails."""

    certification = Certification.fetch_by_id(db, id)
    
    return success_response(
        message=f"Fetched certification successfully",
        status_code=200,
        data=certification.to_dict()
    )


@certification_router.patch("/{id}", status_code=200, response_model=success_response)
async def update_certification(
    id: str,
    payload: certification_schemas.UpdateCertification,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to update a certification"""
    
    if payload.position:
        Certification.move_to_position(db, id, payload.position)

    certification = Certification.update(
        db=db,
        id=id,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'Certification with id {certification.id} updated')

    return success_response(
        message=f"Certification updated successfully",
        status_code=200,
        data=certification.to_dict()
    )


@certification_router.delete("/{id}", status_code=200, response_model=success_response)
async def delete_certification(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to delete a certification"""

    Certification.soft_delete(db, id)

    return success_response(
        message=f"Deleted successfully",
        status_code=200
    )

