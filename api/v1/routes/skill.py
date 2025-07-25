from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import sqlalchemy as sa

from api.db.database import get_db
from api.utils import paginator, helpers
from api.utils.responses import success_response
from api.utils.settings import settings
from api.v1.models.user import User
from api.v1.models.skill import Skill
from api.v1.services.auth import AuthService
from api.v1.services.skill import SkillService
from api.v1.schemas import skill as skill_schemas
from api.utils.loggers import create_logger


skill_router = APIRouter(prefix='/skills', tags=['Skill'])
logger = create_logger(__name__)

@skill_router.post("", status_code=201, response_model=success_response)
async def create_skill(
    payload: skill_schemas.SkillBase,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to create a new skill"""
    
    max_position = Skill.get_max_position(db)

    skill = Skill.create(
        db=db,
        position=max_position+1,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'Skill with id {skill.id} created')

    return success_response(
        message=f"Skill created successfully",
        status_code=201,
        data=skill.to_dict()
    )


@skill_router.get("", status_code=200)
async def get_skills(
    name: str = None,
    page: int = 1,
    per_page: int = 50,
    sort_by: str = 'position',
    order: str = 'asc',
    db: Session=Depends(get_db), 
):
    """Endpoint to get all skills"""

    query, skills, count = Skill.fetch_by_field(
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
        items=[skill.to_dict() for skill in skills],
        endpoint='/skills',
        page=page,
        size=per_page,
        total=count,
    )


@skill_router.get("/{id}", status_code=200, response_model=success_response)
async def get_skill_by_id(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to get a skill by ID or unique_id in case ID fails."""

    skill = Skill.fetch_by_id(db, id)
    
    return success_response(
        message=f"Fetched skill successfully",
        status_code=200,
        data=skill.to_dict()
    )


@skill_router.patch("/{id}", status_code=200, response_model=success_response)
async def update_skill(
    id: str,
    payload: skill_schemas.UpdateSkill,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to update a skill"""
    
    if payload.position:
        Skill.move_to_position(db, id, payload.position)

    skill = Skill.update(
        db=db,
        id=id,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'Skill with id {skill.id} updated')

    return success_response(
        message=f"Skill updated successfully",
        status_code=200,
        data=skill.to_dict()
    )


@skill_router.delete("/{id}", status_code=200, response_model=success_response)
async def delete_skill(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to delete a skill"""

    Skill.soft_delete(db, id)

    return success_response(
        message=f"Deleted successfully",
        status_code=200
    )

