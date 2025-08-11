from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils import paginator, helpers
from api.utils.firebase_service import FirebaseService
from api.utils.responses import success_response
from api.utils.settings import settings
from api.v1.models.user import User
from api.v1.models.profile import Profile
from api.v1.schemas.file import FileBase
from api.v1.services.auth import AuthService
from api.v1.services.profile import ProfileService
from api.v1.services.file import FileService
from api.v1.schemas import profile as profile_schemas
from api.utils.loggers import create_logger


profile_router = APIRouter(prefix='/profile', tags=['Profile'])
logger = create_logger(__name__)

@profile_router.post("", status_code=201, response_model=success_response)
async def create_profile(
    payload: profile_schemas.ProfileBase = Depends(profile_schemas.ProfileBase.as_form),
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to create a new profile"""
    
    _, _, count = Profile.fetch_by_field(db, paginate=False)
    if count > 0:
        raise HTTPException(status_code=400, detail="Profile already exists")
    
    # file = await FileService.upload_file(
    #     db=db,
    #     payload= FileBase(
    #         file=payload.file,
    #         model_name='profile',
    #         model_id=current_user.id,
    #         label='Profile',
    #         description='User profile image'
    #     ),
    #     allowed_extensions=['jpg', 'jpeg', 'png', 'jfif', 'svg']
    # )
    
    _, url = await FirebaseService.upload_file(
        db=db,
        file=payload.file,
        upload_folder='profile',
        model_id=current_user.id,
        file_label="Profile",
        file_description="User profile image",
        allowed_extensions=[
            "jpg", "jpeg", "png", 
            "jfif", "svg", "pdf"
        ],
        add_to_db=True
    )

    profile = Profile.create(
        db=db,
        image_url=url,
        **payload.model_dump(exclude_unset=True, exclude=['file'])
    )

    logger.info(f'Profile with id {profile.id} created')

    return success_response(
        message=f"Profile created successfully",
        status_code=201,
        data=profile.to_dict()
    )


@profile_router.get("", status_code=200, response_model=success_response)
async def get_profile(
    db: Session=Depends(get_db), 
):
    """Endpoint to get profile."""

    _, profiles, count = Profile.fetch_by_field(db, paginate=False)
    
    if count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")

    return success_response(
        message=f"Fetched profile successfully",
        status_code=200,
        data=profiles[0].to_dict()
    )


@profile_router.patch("", status_code=200, response_model=success_response)
async def update_profile(
    payload: profile_schemas.UpdateProfile = Depends(profile_schemas.UpdateProfile.as_form),
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to update a profile"""
    
    _, profiles, count = Profile.fetch_by_field(db, paginate=False)
    
    if count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if payload.file:
        # file = await FileService.upload_file(
        #     db=db,
        #     payload= FileBase(
        #         file=payload.file,
        #         model_name='profile',
        #         model_id=current_user.id,
        #         label='Profile',
        #         description='User profile image'
        #     ),
        #     allowed_extensions=['jpg', 'jpeg', 'png', 'jfif', 'svg']
        # )

        _, url = await FirebaseService.upload_file(
            db=db,
            file=payload.file,
            upload_folder='profile',
            model_id=current_user.id,
            file_label="Profile",
            file_description="User profile image",
            allowed_extensions=[
                "jpg", "jpeg", "png", 
                "jfif", "svg", "pdf"
            ],
            add_to_db=True
        )
        
    profile = Profile.update(
        db=db,
        id=profiles[0].id,
        image_url=url if payload.file else profiles[0].image_url,
        **payload.model_dump(exclude_unset=True, exclude=['file'])
    )

    logger.info(f'Profile with id {profile.id} updated')

    return success_response(
        message=f"Profile updated successfully",
        status_code=200,
        data=profile.to_dict()
    )


@profile_router.delete("", status_code=200, response_model=success_response)
async def delete_profile(
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to delete a profile"""
    
    _, profiles, count = Profile.fetch_by_field(db, paginate=False)
    
    if count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")

    Profile.soft_delete(db, profiles[0].id)

    return success_response(
        message=f"Deleted successfully",
        status_code=200
    )
