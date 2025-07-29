from fastapi import APIRouter, Depends
from slugify import slugify
from sqlalchemy.orm import Session
import sqlalchemy as sa

from api.db.database import get_db
from api.utils import paginator, helpers
from api.utils.responses import success_response
from api.utils.settings import settings
from api.v1.models.user import User
from api.v1.models.project import Project
from api.v1.models.tag import Tag
from api.v1.services.auth import AuthService
from api.v1.services.project import ProjectService
from api.v1.schemas import project as project_schemas
from api.utils.loggers import create_logger


project_router = APIRouter(prefix='/projects', tags=['Project'])
logger = create_logger(__name__)

@project_router.post("", status_code=201, response_model=success_response)
async def create_project(
    payload: project_schemas.ProjectBase,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to create a new project"""
    
    max_position = Project.get_max_position(db)
    
    if payload.technical_details:
        payload.technical_details = helpers.format_additional_info_create(payload.technical_details)
        
    if payload.challenges_and_solutions:
        payload.challenges_and_solutions = helpers.format_additional_info_create(payload.challenges_and_solutions)
        
    project = Project.create(
        db=db,
        slug=" ",
        position=max_position+1,
        **payload.model_dump(exclude_unset=True)
    )
    
    project.slug = slugify(f"{project.unique_id}-{project.name}")
    db.commit()

    logger.info(f'Project with id {project.id} created')

    return success_response(
        message=f"Project created successfully",
        status_code=201,
        data=project.to_dict()
    )


@project_router.get("", status_code=200)
async def get_projects(
    name: str = None,
    domain: str = None,
    slug: str = None,
    project_type: str = None,
    tags: str = None,
    page: int = 1,
    per_page: int = 10,
    sort_by: str = 'position',
    order: str = 'asc',
    db: Session=Depends(get_db)
):
    """Endpoint to get all projects"""

    query, projects, count = Project.fetch_by_field(
        db, 
        sort_by=sort_by,
        order=order.lower(),
        page=page,
        per_page=per_page,
        search_fields={
            'name': name,
        },
        domain=domain,
        slug=slug,
        project_type=project_type,
    )
    
    if tags:
        tag_list = tags.split(',')
        query = query.filter(Project.tags.any(Tag.name.in_(tag_list)))
        projects, count = query.all(), query.count()
    
    return paginator.build_paginated_response(
        items=[project.to_dict() for project in projects],
        endpoint='/projects',
        page=page,
        size=per_page,
        total=count,
    )
    

@project_router.get("/featured", status_code=200)
async def get_featured_projects(
    db: Session=Depends(get_db)
):
    """Endpoint to get all projects"""

    query, projects, count = Project.fetch_by_field(
        db, 
        sort_by='position',
        order='asc',
        page=1,
        per_page=4,
    )
    
    return paginator.build_paginated_response(
        items=[project.to_dict() for project in projects],
        endpoint='/projects/featured',
        page=1,
        size=4,
        total=count,
    )


@project_router.get("/{id}", status_code=200, response_model=success_response)
async def get_project_by_id(
    id: str,
    db: Session=Depends(get_db), 
):
    """Endpoint to get a project by ID or unique_id in case ID fails."""

    project = Project.fetch_by_id(db, id)
    
    return success_response(
        message=f"Fetched project successfully",
        status_code=200,
        data=project.to_dict()
    )


@project_router.patch("/{id}", status_code=200, response_model=success_response)
async def update_project(
    id: str,
    payload: project_schemas.UpdateProject,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to update a project"""
    
    if payload.position:
        Project.move_to_position(db, id, payload.position)

    project = Project.update(
        db=db,
        id=id,
        **payload.model_dump(exclude_unset=True, exclude={'technical_details', 'challenges_and_solutions'})
    )
    
    if payload.technical_details:
        project.technical_details = helpers.format_additional_info_update(
            additional_info=payload.technical_details,
            model_instance=project,
            model_instance_additional_info_name='technical_details',
            keys_to_remove=payload.technical_details_keys_to_remove
        )
    
    if payload.challenges_and_solutions:
        project.challenges_and_solutions = helpers.format_additional_info_update(
            additional_info=payload.challenges_and_solutions,
            model_instance=project,
            model_instance_additional_info_name='challenges_and_solutions',
            keys_to_remove=payload.challenges_and_solutions_keys_to_remove
        )
        
    db.commit()

    logger.info(f'Project with id {project.id} updated')

    return success_response(
        message=f"Project updated successfully",
        status_code=200,
        data=project.to_dict()
    )


@project_router.delete("/{id}", status_code=200, response_model=success_response)
async def delete_project(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to delete a project"""

    Project.soft_delete(db, id)

    return success_response(
        message=f"Deleted successfully",
        status_code=200
    )

