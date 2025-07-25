from fastapi import APIRouter

from api.v1.routes.auth import auth_router
from api.v1.routes.user import user_router
from api.v1.routes.award import award_router
from api.v1.routes.blog import blog_router
from api.v1.routes.category import category_router
from api.v1.routes.certification import certification_router
from api.v1.routes.education import education_router
from api.v1.routes.experience import experience_router
from api.v1.routes.file import file_router
from api.v1.routes.message import message_router
from api.v1.routes.project import project_router
from api.v1.routes.service import service_router
from api.v1.routes.skill import skill_router
from api.v1.routes.tag import tag_router
from api.v1.routes.testimonial import testimonial_router
from api.v1.routes.profile import profile_router

v1_router = APIRouter(prefix='/api/v1')

# Register all routes
v1_router.include_router(auth_router)
v1_router.include_router(user_router)
v1_router.include_router(profile_router)
v1_router.include_router(award_router)
v1_router.include_router(blog_router)
v1_router.include_router(category_router)
v1_router.include_router(certification_router)
v1_router.include_router(education_router)
v1_router.include_router(experience_router)
v1_router.include_router(file_router)
v1_router.include_router(message_router)
v1_router.include_router(project_router)
v1_router.include_router(service_router)
v1_router.include_router(skill_router)
v1_router.include_router(tag_router)
v1_router.include_router(testimonial_router)
