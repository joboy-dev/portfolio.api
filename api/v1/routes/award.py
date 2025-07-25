from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils import paginator, helpers
from api.utils.responses import success_response
from api.utils.settings import settings
from api.v1.models.user import User
from api.v1.models.award import Award
from api.v1.services.auth import AuthService
from api.v1.services.award import AwardService
from api.v1.schemas import award as award_schemas
from api.utils.loggers import create_logger


award_router = APIRouter(prefix='/awards', tags=['Award'])
logger = create_logger(__name__)

@award_router.post("", status_code=201, response_model=success_response)
async def create_award(
    payload: award_schemas.AwardBase,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to create a new award"""

    award = Award.create(
        db=db,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'Award with id {award.id} created')

    return success_response(
        message=f"Award created successfully",
        status_code=201,
        data=award.to_dict()
    )


@award_router.get("", status_code=200)
async def get_awards(
    name: str = None,
    page: int = 1,
    per_page: int = 30,
    sort_by: str = 'issue_date',
    order: str = 'desc',
    db: Session=Depends(get_db), 
):
    """Endpoint to get all awards"""

    query, awards, count = Award.fetch_by_field(
        db, 
        sort_by=sort_by,
        order=order.lower(),
        page=page,
        per_page=per_page,
        search_fields={'name': name},
    )
    
    return paginator.build_paginated_response(
        items=[award.to_dict() for award in awards],
        endpoint='/awards',
        page=page,
        size=per_page,
        total=count,
    )


@award_router.get("/{id}", status_code=200, response_model=success_response)
async def get_award_by_id(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to get a award by ID or unique_id in case ID fails."""

    award = Award.fetch_by_id(db, id)
    
    return success_response(
        message=f"Fetched award successfully",
        status_code=200,
        data=award.to_dict()
    )


@award_router.patch("/{id}", status_code=200, response_model=success_response)
async def update_award(
    id: str,
    payload: award_schemas.UpdateAward,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to update a award"""

    award = Award.update(
        db=db,
        id=id,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'Award with id {award.id} updated')

    return success_response(
        message=f"Award updated successfully",
        status_code=200,
        data=award.to_dict()
    )


@award_router.delete("/{id}", status_code=200, response_model=success_response)
async def delete_award(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to delete a award"""

    Award.soft_delete(db, id)

    return success_response(
        message=f"Deleted successfully",
        status_code=200
    )

