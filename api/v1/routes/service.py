from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils import paginator, helpers
from api.utils.responses import success_response
from api.utils.settings import settings
from api.v1.models.user import User
from api.v1.models.service import Service
from api.v1.services.auth import AuthService
from api.v1.services.service import ServiceService
from api.v1.schemas import service as service_schemas
from api.utils.loggers import create_logger


service_router = APIRouter(prefix='/services', tags=['Service'])
logger = create_logger(__name__)

@service_router.post("", status_code=201, response_model=success_response)
async def create_service(
    payload: service_schemas.ServiceBase,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to create a new service"""

    service = Service.create(
        db=db,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'Service with id {service.id} created')

    return success_response(
        message=f"Service created successfully",
        status_code=201,
        data=service.to_dict()
    )


@service_router.get("", status_code=200)
async def get_services(
    name: str = None,
    page: int = 1,
    per_page: int = 20,
    sort_by: str = 'created_at',
    order: str = 'desc',
    db: Session=Depends(get_db), 
):
    """Endpoint to get all services"""

    query, services, count = Service.fetch_by_field(
        db, 
        sort_by=sort_by,
        order=order.lower(),
        page=page,
        per_page=per_page,
        search_fields={
            'name': name,
        },
    )
    
    return paginator.build_paginated_response(
        items=[service.to_dict() for service in services],
        endpoint='/services',
        page=page,
        size=per_page,
        total=count,
    )


@service_router.get("/{id}", status_code=200, response_model=success_response)
async def get_service_by_id(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to get a service by ID or unique_id in case ID fails."""

    service = Service.fetch_by_id(db, id)
    
    return success_response(
        message=f"Fetched service successfully",
        status_code=200,
        data=service.to_dict()
    )


@service_router.patch("/{id}", status_code=200, response_model=success_response)
async def update_service(
    id: str,
    payload: service_schemas.UpdateService,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to update a service"""

    service = Service.update(
        db=db,
        id=id,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'Service with id {service.id} updated')

    return success_response(
        message=f"Service updated successfully",
        status_code=200,
        data=service.to_dict()
    )


@service_router.delete("/{id}", status_code=200, response_model=success_response)
async def delete_service(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to delete a service"""

    Service.soft_delete(db, id)

    return success_response(
        message=f"Deleted successfully",
        status_code=200,
        data={'id': id}
    )

