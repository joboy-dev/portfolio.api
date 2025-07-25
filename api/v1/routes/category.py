from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils import paginator, helpers
from api.utils.responses import success_response
from api.utils.settings import settings
from api.v1.models.user import User
from api.v1.models.category import Category
from api.v1.services.auth import AuthService
from api.v1.services.category import CategoryService
from api.v1.schemas import category as category_schemas
from api.utils.loggers import create_logger


category_router = APIRouter(prefix='/categories', tags=['Category'])
logger = create_logger(__name__)

@category_router.post("", status_code=201, response_model=success_response)
async def create_category(
    payload: category_schemas.CategoryBase,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to create a new category"""
    
    if not payload.slug:
        payload.slug = slugify(payload.name)

    category = Category.create(
        db=db,
        **payload.model_dump(exclude_unset=True)
    )

    return success_response(
        message=f"Category created successfully",
        status_code=200,
        data=category.to_dict()
    )


@category_router.get("", status_code=200)
async def get_categories(
    unique_id: str = None,
    name: str = None,
    slug: str = None,
    model_type: str = None,
    page: int = 1,
    per_page: int = 25,
    sort_by: str = 'created_at',
    order: str = 'desc',
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to get all categories"""

    query, categories, count = Category.fetch_by_field(
        db, 
        sort_by=sort_by,
        order=order.lower(),
        page=page,
        per_page=per_page,
        search_fields={
            'name': name,
            'unique_id': unique_id,
        },
        slug=slug,
        model_type=model_type,
    )
    
    return paginator.build_paginated_response(
        items=[category.to_dict() for category in categories],
        endpoint='/categories',
        page=page,
        size=per_page,
        total=count,
    )
    

@category_router.post("/attach", status_code=201, response_model=success_response)
async def attach_category_to_eneity(
    payload: category_schemas.AttachOrDetatchCategory,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to attach a category to an entity"""

    CategoryService.create_category_association(
        db=db,
        category_ids=payload.category_ids,
        model_type=payload.model_type,
        entity_id=payload.entity_id
    )

    return success_response(
        message=f"Categories attached to entity successfully",
        status_code=200
    )
    

@category_router.post("/detatch", status_code=201, response_model=success_response)
async def detatch_category_from_entity(
    
    payload: category_schemas.AttachOrDetatchCategory,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to detatch a category from an entity"""
    
    CategoryService.delete_category_association(
        db=db,
        category_ids=payload.category_ids,
        model_type=payload.model_type,
        entity_id=payload.entity_id
    )

    return success_response(
        message=f"Categories detatched from entity successfully",
        status_code=200
    )


@category_router.get("/{id}", status_code=200, response_model=success_response)
async def get_category_by_id(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to get a category by ID or unique_id in case ID fails."""

    category = Category.fetch_by_id(db, id)
    
    return success_response(
        message=f"Fetched category successfully",
        status_code=200,
        data=category.to_dict()
    )


@category_router.patch("/{id}", status_code=200, response_model=success_response)
async def update_category(
    id: str,
    payload: category_schemas.UpdateCategory,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to update a category"""
    
    prev_category = Category.fetch_by_id(db, id)

    category = Category.update(
        db=db,
        id=id,
        **payload.model_dump(exclude_unset=True)
    )

    return success_response(
        message=f"Category updated successfully",
        status_code=200,
        data=category.to_dict()
    )


@category_router.delete("/{id}", status_code=200, response_model=success_response)
async def delete_category(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to delete a category"""

    Category.soft_delete(db, id)

    return success_response(
        message=f"Deleted successfully",
        status_code=200,
        data={"id": id}
    )

