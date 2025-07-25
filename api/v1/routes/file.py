import os
from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils import paginator
from api.utils.firebase_service import FirebaseService
from api.utils.minio_service import MinioService
from api.utils.responses import success_response
from api.v1.models.user import User
from api.v1.models.file import File as FileModel
from api.v1.services.auth import AuthService
from api.v1.services.file import FileService
from api.v1.schemas import file as file_schemas
from api.utils.loggers import create_logger


file_router = APIRouter(tags=['Files & Folders'])
logger = create_logger(__name__)

@file_router.post("/files", status_code=201, response_model=success_response)
async def create_file(
    payload: file_schemas.FileBase = Depends(file_schemas.FileBase.as_form),
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to create a new file

    Args:
        payload: Payload for creating a new file.
        db (Session, optional): DB session. Defaults to Depends(get_db).
        current_user (User, optional): Current logged in user for authentication. Defaults to Depends(AuthService.get_current_entity).
    """
    
    file_obj = await FileService.upload_file(
        db=db,
        payload=payload
    )
    
    logger.info(f'File {file_obj.file_name} created at {file_obj.file_path}')

    return success_response(
        message=f"File created successfully",
        status_code=201,
        data=file_obj.to_dict()
    )
    

@file_router.post("/files/bulk-upload", status_code=201, response_model=success_response)
async def bulk_upload_files(
    payload: file_schemas.BulkUploadFile = Depends(file_schemas.BulkUploadFile.as_form),
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to bulk upload files
    
    Args:
        payload: Payload for bulk uploading files.
        db (Session, optional): DB session. Defaults to Depends(get_db).
        current_user (User, optional): Current logged in user for authentication. Defaults to Depends(AuthService.get_current_entity).
    """

    file_objs = await FileService.bulk_upload(
        db=db,
        files=payload.files,
        model_id=payload.model_id,
        model_name=payload.model_name
    )
    
    logger.info(f'Files {[file.id for file in file_objs]} uploaded successfully')
    
    return success_response(
        message=f"Files uploaded successfully",
        status_code=201,
        data=[file.to_dict() for file in file_objs]
    )


@file_router.post("/files/minio-upload", status_code=201, response_model=success_response)
async def upload_file_to_minio(
    payload: file_schemas.FileBase = Depends(file_schemas.FileBase.as_form),
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to create a new file

    Args:
        payload: Payload for creating a new file.
        db (Session, optional): DB session. Defaults to Depends(get_db).
        current_user (User, optional): Current logged in user for authentication. Defaults to Depends(AuthService.get_current_entity).
    """
    
    url = await MinioService.upload_to_minio(
        db=db,
        file=payload.file,
        model_name=payload.model_name,
        model_id=payload.model_id,
        file_label=payload.label,
        file_description=payload.description,
        allowed_extensions=[
            "jpg", "jpeg", "png", 
            "jfif", "svg", "pdf"
        ]
    )
    
    return success_response(
        message=f"File uplaoded successfully",
        status_code=201,
        data={'url': url}
    )
    

@file_router.post("/files/firebase-upload", status_code=201, response_model=success_response)
async def upload_file_to_firebase(
    payload: file_schemas.FileBase = Depends(file_schemas.FileBase.as_form),
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to create a new file

    Args:
        payload: Payload for creating a new file.
        db (Session, optional): DB session. Defaults to Depends(get_db).
        current_user (User, optional): Current logged in user for authentication. Defaults to Depends(AuthService.get_current_entity).
    """
    
    url = await FirebaseService.upload_file(
        db=db,
        file=payload.file,
        upload_folder=payload.model_name,
        model_id=payload.model_id,
        file_label=payload.label,
        file_description=payload.description,
        allowed_extensions=[
            "jpg", "jpeg", "png", 
            "jfif", "svg", "pdf"
        ]
    )
    
    return success_response(
        message=f"File uplaoded successfully",
        status_code=201,
        data={'url': url}
    )


@file_router.get("/files", status_code=200)
async def get_files(
    model_name: str = None,
    model_id: str = None,
    file_name: str = None,
    label: str = None,
    page: int = 1,
    per_page: int = 50,
    sort_by: str = 'position',
    order: str = 'asc',
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to get all files

    Args:
        db (Session, optional): DB session. Defaults to Depends(get_db).
        entity (User, optional): Current logged in user for authentication. Defaults to Depends(AuthService.get_current_entity).
    """
    
    query, files, count = FileModel.fetch_by_field(
        db, 
        sort_by=sort_by,
        order=order.lower(),
        page=page,
        per_page=per_page,
        search_fields={
            'file_name': file_name,
            'label': label,
        },
        model_name=model_name,
        model_id=model_id,
    )
    
    return paginator.build_paginated_response(
        items=[file.to_dict() for file in files],
        endpoint='/files',
        page=page,
        size=per_page,
        total=count,
    )


@file_router.get("/files/{id}", status_code=200, response_model=success_response)
async def get_file_by_id(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to get a file by ID or unique_id in case ID fails.
    Args:
        id (str): ID of the file to retrieve.
        db (Session, optional): DB session. Defaults to Depends(get_db).
        current_user (User, optional): Current logged in user for authentication. Defaults to Depends(AuthService.get_current_entity).
    """

    file = FileModel.fetch_by_id(db, id)
    
    return success_response(
        message=f"Fetched file successfully",
        status_code=200,
        data=file.to_dict()
    )


@file_router.patch("/files/{id}", status_code=200, response_model=success_response)
async def update_file(
    id: str,
    payload: file_schemas.UpdateFile = Depends(file_schemas.UpdateFile.as_form),
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to update a file

    Args:
        id (str): ID of the file to update.
        payload: Payload for updating the file.
        db (Session, optional): DB session. Defaults to Depends(get_db).
        entity (User, optional): Current logged in user for authentication. Defaults to Depends(AuthService.get_current_entity).
    """

    file_instance = FileModel.fetch_by_id(db, id)
    
    if payload.position:
        FileService.move_file_to_position(
            db=db, file_id=file_instance.id,
            new_position=payload.position
        )
    
    # if payload.file:
    #     file_obj = await FileService.upload_file(
    #         db=db,
    #         payload=file_schemas.FileBase(
    #             file=payload.file,
    #             model_name=file_instance.model_name,
    #             model_id=file_instance.model_id,
    #             description=payload.description if payload.description else None,
    #             label=payload.label if payload.label else None
    #         ),
    #         add_to_db=False
    #     )
    #     os.remove(file_instance.file_path)
        
    #     updated_file = FileModel.update(
    #         db=db,
    #         id=id,
    #         file_name=file_obj['file_name'],
    #         file_path=file_obj['file_path'],
    #         file_size=file_obj['file_size'],
    #         url=file_obj['url'],
    #         description=payload.description if payload.description else None,
    #         label=payload.label if payload.label else None
    #         # **file_obj,
    #     )
         
    # else:
    updated_file = FileModel.update(
        db=db,
        id=id,
        **payload.model_dump(exclude_unset=True)
    )

    logger.info(f'File updated to {updated_file.file_name} at {updated_file.file_path}')
    
    return success_response(
        message=f"File updated successfully",
        status_code=200,
        data=updated_file.to_dict()
    )


@file_router.delete("/files/{id}", status_code=200, response_model=success_response)
async def delete_file(
    id: str,
    db: Session=Depends(get_db), 
    current_user: User=Depends(AuthService.get_current_superuser)
):
    """Endpoint to delete a file

    Args:
        id (str): ID of the file to delete.
        db (Session, optional): DB session. Defaults to Depends(get_db).
        current_user (User, optional): Current logged in user for authentication. Defaults to Depends(AuthService.get_current_entity).
    """
    
    file = FileModel.fetch_by_id(db, id)
    os.remove(file.file_path)
    FileModel.hard_delete(db, id)

    return success_response(
        message=f"Deleted {id} successfully",
        status_code=200,
        data={"id": id}
    )
