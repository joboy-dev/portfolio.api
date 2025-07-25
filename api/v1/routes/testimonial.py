from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from decouple import config
import sqlalchemy as sa

from api.core.dependencies.email_sending_service import send_email
from api.db.database import get_db
from api.utils import paginator, helpers
from api.utils.responses import success_response
from api.utils.settings import settings
from api.v1.models.user import User
from api.v1.models.testimonial import Testimonial
from api.v1.services.auth import AuthService
from api.v1.services.testimonial import TestimonialService
from api.v1.schemas import testimonial as testimonial_schemas
from api.utils.loggers import create_logger


testimonial_router = APIRouter(prefix='/testimonials', tags=['Testimonial'])
logger = create_logger(__name__)

@testimonial_router.post("", status_code=201, response_model=success_response)
async def create_testimonial(
    bg_tasks: BackgroundTasks,
    payload: testimonial_schemas.TestimonialBase,
    db: Session=Depends(get_db), 
):
    """Endpoint to create a new testimonial"""
    
    max_position = Testimonial.get_max_position(db)

    testimonial = Testimonial.create(
        db=db,
        position=max_position+1,
        **payload.model_dump(exclude_unset=True)
    )
    
    # Send message to email
    bg_tasks.add_task(
        send_email,
        recipients=[config("MAIL_TO")],
        subject="You Have a New Testimonial Message",
        template_name="new-testimonial.html" ,
        template_data={
            "name": payload.name,
            "title": payload.title,
            "message": payload.message,
            "rating": payload.rating,
        }
    )


    logger.info(f'Testimonial with id {testimonial.id} created')

    return success_response(
        message=f"Testimonial created successfully",
        status_code=201,
        data=testimonial.to_dict()
    )


@testimonial_router.get("", status_code=200)
async def get_testimonials(
    name: str = None,
    is_published: bool = None,
    page: int = 1,
    per_page: int = 10,
    sort_by: str = 'created_at',
    order: str = 'desc',
    db: Session=Depends(get_db), 
):
    """Endpoint to get all testimonials"""

    query, testimonials, count = Testimonial.fetch_by_field(
        db, 
        sort_by=sort_by,
        order=order.lower(),
        page=page,
        per_page=per_page,
        search_fields={
            'name': name,
        },
        is_published=is_published
    )
    
    return paginator.build_paginated_response(
        items=[testimonial.to_dict() for testimonial in testimonials],
        endpoint='/testimonials',
        page=page,
        size=per_page,
        total=count,
    )


@testimonial_router.get("/{id}", status_code=200, response_model=success_response)
async def get_testimonial_by_id(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to get a testimonial by ID or unique_id in case ID fails."""

    testimonial = Testimonial.fetch_by_id(db, id)
    
    return success_response(
        message=f"Fetched testimonial successfully",
        status_code=200,
        data=testimonial.to_dict()
    )


@testimonial_router.patch("/{id}", status_code=200, response_model=success_response)
async def update_testimonial(
    id: str,
    payload: testimonial_schemas.UpdateTestimonial,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to update a testimonial"""
    
    if payload.position:
        Testimonial.move_to_position(db, id, payload.position)

    testimonial = Testimonial.update(
        db=db,
        id=id,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'Testimonial with id {testimonial.id} updated')

    return success_response(
        message=f"Testimonial updated successfully",
        status_code=200,
        data=testimonial.to_dict()
    )


@testimonial_router.delete("/{id}", status_code=200, response_model=success_response)
async def delete_testimonial(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to delete a testimonial"""

    Testimonial.soft_delete(db, id)

    return success_response(
        message=f"Deleted successfully",
        status_code=200
    )

