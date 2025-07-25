import os, pyrebase
from sqlalchemy.orm import Session
from decouple import config

from api.core.dependencies.firebase_config import firebase_config
from api.v1.models.file import File
from api.v1.schemas.file import FileBase
from api.v1.services.file import FileService


class FirebaseService:
    
    @classmethod
    async def upload_file(
        cls, 
        db: Session,
        file,
        allowed_extensions: list | None, 
        upload_folder: str, 
        model_id: str = None,
        file_label: str = None,
        file_description: str = None,
        add_to_db: bool = False,
    ):
        '''Function to upload a file'''
        
        new_file = await FileService.upload_file(
            db=db,
            payload=FileBase(
                file=file,
                model_id=model_id,
                model_name=upload_folder,
                label=file_label,
                description=file_description
            ),
            allowed_extensions=allowed_extensions,
            add_to_db=add_to_db
        )
        
        # Initailize firebase
        firebase = pyrebase.initialize_app(firebase_config)
        
        # Set up storage and a storage path for each file
        storage = firebase.storage()
        firebase_storage_path = (
            f'{config("APP_NAME")}/{upload_folder}/{model_id}/{new_file.file_name}' 
            if model_id 
            else f'{config("APP_NAME")}/{upload_folder}/{new_file.file_name}'
        )
        
        # Store the file in the firebase storage path
        storage.child(firebase_storage_path).put(new_file.file_path)
        
        # Get download URL
        download_url = storage.child(firebase_storage_path).get_url(None)
        
        if isinstance(new_file, File):
            # Update file url
            File.update(
                db=db,
                id=new_file.id,
                url=download_url
            )
        
        return download_url
