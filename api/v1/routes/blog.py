from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from slugify import slugify
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils import paginator, helpers
from api.utils.backblaze_service import BackblazeService
from api.utils.responses import success_response
from api.utils.settings import settings
from api.v1.models.user import User
from api.v1.models.blog import Blog
from api.v1.models.tag import Tag
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

    max_position = Blog.get_max_position(db)

    blog = Blog.create(
        db=db,
        slug=" ",
        position=max_position+1,
        published_at=datetime.now(timezone.utc) if payload.is_published else None,
        **payload.model_dump(exclude_unset=True)
    )

    blog.slug = slugify(f"{blog.unique_id}-{blog.title}")
    db.commit()

    logger.info(f'Blog with id {blog.id} created')

    return success_response(
        message=f"Blog created successfully",
        status_code=201,
        data=blog.to_dict()
    )


@blog_router.get("", status_code=200)
async def get_blogs(
    search: str = None,
    is_published: bool = None,
    tags: str = None,
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
            'title': search,
        },
        is_published=is_published,
    )

    if tags:
        tag_list = tags.split(',')
        query = query.filter(Blog.tags.any(Tag.name.in_(tag_list)))
        blogs, count = query.all(), query.count()

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

    if payload.position:
        Blog.move_to_position(db, id, payload.position)

    blog = Blog.update(
        db=db,
        id=id,
        **payload.model_dump(exclude_unset=True, exclude={'position'})
    )

    if payload.is_published and not blog.published_at:
        blog.published_at = datetime.now(timezone.utc)
        db.commit()

    logger.info(f'Blog with id {blog.id} updated')

    return success_response(
        message=f"Blog updated successfully",
        status_code=200,
        data=blog.to_dict()
    )


@blog_router.post("/{id}/cover-image", status_code=200, response_model=success_response)
async def upload_blog_cover_image(
    id: str,
    payload: blog_schemas.BlogCoverImage = Depends(blog_schemas.BlogCoverImage.as_form),
    db: Session=Depends(get_db),
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to upload/replace a blog's cover image"""

    blog = Blog.fetch_by_id(db, id)

    _, url = await BackblazeService.upload_to_backblaze(
        db=db,
        file=payload.file,
        model_name='blogs',
        model_id=blog.id,
        file_label="Cover Image",
        file_description="Blog cover image",
        allowed_extensions=[
            "jpg", "jpeg", "png",
            "jfif", "svg"
        ],
        add_to_db=True
    )

    blog = Blog.update(
        db=db,
        id=id,
        cover_image_url=url
    )

    return success_response(
        message=f"Blog cover image uploaded successfully",
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
