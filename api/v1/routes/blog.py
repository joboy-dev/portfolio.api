from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils import paginator, helpers
from api.utils.responses import success_response
from api.utils.settings import settings
from api.v1.models.user import User
from api.v1.models.blog import Blog
from api.v1.services.auth import AuthService
from api.v1.services.blog import BlogService
from api.v1.schemas import blog as blog_schemas
from api.utils.loggers import create_logger


blog_router = APIRouter(prefix='/blogs', tags=['Blog'])
logger = create_logger(__name__)

@blog_router.post("", status_code=201, response_model=success_response)
async def create_blog(
    payload: blog_schemas.BlogBase,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to create a new blog"""

    blog = Blog.create(
        db=db,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'Blog with id {blog.id} created')

    return success_response(
        message=f"Blog created successfully",
        status_code=201,
        data=blog.to_dict()
    )


@blog_router.get("", status_code=200)
async def get_blogs(
    search: str = None,
    page: int = 1,
    per_page: int = 10,
    sort_by: str = 'created_at',
    order: str = 'desc',
    db: Session=Depends(get_db), 
):
    """Endpoint to get all blogs"""

    query, blogs, count = Blog.fetch_by_field(
        db, 
        sort_by=sort_by,
        order=order.lower(),
        page=page,
        per_page=per_page,
        search_fields={
            # 'email': search,
        },
    )
    
    return paginator.build_paginated_response(
        items=[blog.to_dict() for blog in blogs],
        endpoint='/blogs',
        page=page,
        size=per_page,
        total=count,
    )


@blog_router.get("/{id}", status_code=200, response_model=success_response)
async def get_blog_by_id(
    id: str,
    db: Session=Depends(get_db), 
):
    """Endpoint to get a blog by ID or unique_id in case ID fails."""

    blog = Blog.fetch_by_id(db, id)
    
    return success_response(
        message=f"Fetched blog successfully",
        status_code=200,
        data=blog.to_dict()
    )


@blog_router.patch("/{id}", status_code=200, response_model=success_response)
async def update_blog(
    id: str,
    payload: blog_schemas.UpdateBlog,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to update a blog"""

    blog = Blog.update(
        db=db,
        id=id,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'Blog with id {blog.id} updated')

    return success_response(
        message=f"Blog updated successfully",
        status_code=200,
        data=blog.to_dict()
    )


@blog_router.delete("/{id}", status_code=200, response_model=success_response)
async def delete_blog(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to delete a blog"""

    Blog.soft_delete(db, id)

    return success_response(
        message=f"Deleted successfully",
        status_code=200
    )

