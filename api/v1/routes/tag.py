from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils import paginator, helpers
from api.utils.cache import get_cache
from api.utils.responses import success_response
from api.utils.settings import settings
from api.v1.models.user import User
from api.v1.models.tag import Tag
from api.v1.services.auth import AuthService
from api.v1.services.tag import TagService
from api.v1.schemas import tag as tag_schemas
from api.utils.loggers import create_logger


tag_router = APIRouter(prefix='/tags', tags=['Tag'])
logger = create_logger(__name__)
tag_cache = get_cache('tags')

@tag_router.post("", status_code=201, response_model=success_response)
async def create_tag(
    payload: tag_schemas.TagBase,
    db: Session=Depends(get_db),
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to create a new tag"""

    payload.name = payload.name.lower()
    payload.model_type = payload.model_type.lower()

    existing_tag = Tag.fetch_one_by_field(
        db=db,
        throw_error=False,
        name=payload.name,
        model_type=payload.model_type
    )

    if existing_tag:
        raise HTTPException(400, detail="Tag already exists")

    tag = Tag.create(
        db=db,
        **payload.model_dump(exclude_unset=True)
    )

    tag_cache.clear()

    return success_response(
        message=f"Tag created successfully",
        status_code=200,
        data=tag.to_dict()
    )


@tag_router.get("", status_code=200)
async def get_tags(
    name: str = None,
    group: str = None,
    model_type: str = None,
    page: int = 1,
    per_page: int = 25,
    sort_by: str = 'created_at',
    order: str = 'desc',
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to get all tags"""

    use_cache = (
        not name and not group and not model_type
        and sort_by == 'created_at' and order.lower() == 'desc'
    )

    if use_cache and tag_cache.has_page(page, per_page):
        return paginator.build_paginated_response(
            items=tag_cache.get_page(page, per_page),
            endpoint='/tags',
            page=page,
            size=per_page,
            total=tag_cache.total,
        )

    query, tags, count = Tag.fetch_by_field(
        db,
        sort_by=sort_by,
        order=order.lower(),
        page=page,
        per_page=per_page,
        search_fields={
            'name': name,
        },
        group=group,
        model_type=model_type,
    )

    items = [tag.to_dict() for tag in tags]

    if use_cache:
        tag_cache.store_page(items, count, 'id', 'unique_id')

    return paginator.build_paginated_response(
        items=items,
        endpoint='/tags',
        page=page,
        size=per_page,
        total=count,
    )
    

@tag_router.post("/attach", status_code=201, response_model=success_response)
async def attach_tag_to_eneity(
    payload: tag_schemas.AttachOrDetatchTag,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to attach a tag to an entity"""
    
    TagService.create_tag_association(
        db=db,
        tag_ids=payload.tag_ids,
        model_type=payload.model_type,
        entity_id=payload.entity_id
    )

    # the attached entity's own cached `tags` field is now stale
    get_cache(payload.model_type).clear()

    return success_response(
        message=f"Tag(s) attached to entity successfully",
        status_code=200
    )
    

@tag_router.post("/detatch", status_code=201, response_model=success_response)
async def detatch_tag_from_entity(
    payload: tag_schemas.AttachOrDetatchTag,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to detatch a tag from an entity"""
 
    TagService.delete_tag_association(
        db=db,
        tag_ids=payload.tag_ids,
        model_type=payload.model_type,
        entity_id=payload.entity_id
    )

    get_cache(payload.model_type).clear()

    return success_response(
        message=f"Tag(s) detatched from entity successfully",
        status_code=200
    )


@tag_router.get("/{id}", status_code=200, response_model=success_response)
async def get_tag_by_id(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to get a tag by ID or unique_id in case ID fails."""

    cached_tag = tag_cache.get_item(id)
    if cached_tag:
        return success_response(
            message=f"Fetched tag successfully",
            status_code=200,
            data=cached_tag
        )

    tag = Tag.fetch_by_id(db, id)
    tag_dict = tag.to_dict()
    tag_cache.store_item(tag_dict, 'id', 'unique_id')

    return success_response(
        message=f"Fetched tag successfully",
        status_code=200,
        data=tag_dict
    )


@tag_router.patch("/{id}", status_code=200, response_model=success_response)
async def update_tag(
    id: str,
    payload: tag_schemas.UpdateTag,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to update a tag"""
    
    tag = Tag.fetch_by_id(db, id)

    if payload.name:
        existing_tag = Tag.fetch_one_by_field(
            db=db,
            throw_error=False,
            name=payload.name,
            model_type=tag.model_type
        )
        
        if existing_tag and existing_tag.id != id:
            raise HTTPException(400, detail="Tag with this name already exists")
        
        payload.name = payload.name.lower()
    
    if payload.model_type:
        payload.model_type = payload.model_type.lower()
        
    updated_tag = Tag.update(
        db=db,
        id=id,
        **payload.model_dump(exclude_unset=True)
    )

    tag_cache.clear()

    return success_response(
        message=f"Tag updated successfully",
        status_code=200,
        data=updated_tag.to_dict()
    )


@tag_router.delete("/{id}", status_code=200, response_model=success_response)
async def delete_tag(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to delete a tag"""

    Tag.soft_delete(db, id)

    tag_cache.clear()

    return success_response(
        message=f"Deleted successfully",
        status_code=200,
        data={"id": id}
    )

