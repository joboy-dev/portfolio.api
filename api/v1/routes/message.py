from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from decouple import config

from api.core.dependencies.email_sending_service import send_email
from api.db.database import get_db
from api.utils import paginator, helpers
from api.utils.responses import success_response
from api.utils.settings import settings
from api.v1.models.user import User
from api.v1.models.message import Message
from api.v1.services.auth import AuthService
from api.v1.services.message import MessageService
from api.v1.schemas import message as message_schemas
from api.utils.loggers import create_logger


message_router = APIRouter(prefix='/messages', tags=['Message'])
logger = create_logger(__name__)

@message_router.post("/send", status_code=201, response_model=success_response)
async def send_message(
    bg_tasks: BackgroundTasks,
    payload: message_schemas.MessageBase,
    db: Session=Depends(get_db), 
):
    """Endpoint to create a new message"""

    message = Message.create(
        db=db,
        **payload.model_dump(exclude_unset=True)
    )
    
    # Send message to email
    bg_tasks.add_task(
        send_email,
        recipients=[config("MAIL_TO")],
        subject="You Have a New Contact Message",
        template_name="new-message.html" ,
        template_data={
            "name": payload.name,
            "email": payload.email,
            "message": payload.message,
            "location": payload.location,
            "phone_country_code": payload.phone_country_code,
            "phone_number": payload.phone_number,
        }
    )

    logger.info(f'Message with id {message.id} created')

    return success_response(
        message=f"Message sent successfully",
        status_code=201,
        data=message.to_dict()
    )


@message_router.get("", status_code=200)
async def get_messages(
    name: str = None,
    email: str = None,
    page: int = 1,
    per_page: int = 10,
    sort_by: str = 'created_at',
    order: str = 'desc',
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to get all messages"""

    query, messages, count = Message.fetch_by_field(
        db, 
        sort_by=sort_by,
        order=order.lower(),
        page=page,
        per_page=per_page,
        search_fields={
            'name': name,
            'email': email,
        },
    )
    
    return paginator.build_paginated_response(
        items=[message.to_dict() for message in messages],
        endpoint='/messages',
        page=page,
        size=per_page,
        total=count,
    )


@message_router.get("/{id}", status_code=200, response_model=success_response)
async def get_message_by_id(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to get a message by ID or unique_id in case ID fails."""

    message = Message.fetch_by_id(db, id)
    
    return success_response(
        message=f"Fetched message successfully",
        status_code=200,
        data=message.to_dict()
    )


@message_router.delete("/{id}", status_code=200, response_model=success_response)
async def delete_message(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to delete a message"""

    Message.soft_delete(db, id)

    return success_response(
        message=f"Deleted successfully",
        status_code=200
    )

