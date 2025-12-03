import os, pyrebase
from sqlalchemy.orm import Session
from decouple import config

from api.utils.loggers import create_logger
from firebase_config import firebase_config
from api.v1.models.file import File
from api.v1.schemas.file import FileBase
from api.v1.services.file import FileService


logger = create_logger(__name__)

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
        add_to_db: bool = True,
        delete_after_upload: bool = False,
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
            add_to_db=add_to_db,
        )
        
        if isinstance(new_file, File):
            new_file = new_file.to_dict()
        
        # Initailize firebase
        firebase = pyrebase.initialize_app(firebase_config)
            
        # Set up storage and a storage path for each file
        storage = firebase.storage()
        firebase_storage_path = (
            f'{config("APP_NAME")}/{upload_folder}/{model_id}/{new_file.get('file_name')}' 
            if model_id 
            else f'{config("APP_NAME")}/{upload_folder}/{new_file.get('file_name')}'
        )
        
        # Store the file in the firebase storage path
        storage.child(firebase_storage_path).put(new_file.get('file_path'))
        
        # Get download URL
        download_url = storage.child(firebase_storage_path).get_url(None)
        
        logger.info(f"Firebase url:  {download_url}")
        logger.info(f"File id: {new_file.get('id')}")
        
        # Update file url
        if new_file.get('id', None):
            File.update(
                db=db,
                id=new_file.get('id'),
                external_url=download_url,
                url=download_url if delete_after_upload else new_file.get('url')
            )
            
        if delete_after_upload:
            try:
                os.remove(new_file.get('file_path'))
                logger.info(f"Deleted file at {new_file.get('file_path')} after upload")
            except Exception as e:
                logger.error(f"Error deleting file after upload: {e}")
        
        return new_file, download_url


    @classmethod
    def delete_file_from_firebase(cls, storage_path: str):
        """
        Deletes a file from Firebase Storage.

        Args:
            storage_path (str): The path to the file in Firebase Storage (e.g., 'app_name/folder/model_id/filename.ext')
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            firebase = pyrebase.initialize_app(firebase_config)
            storage = firebase.storage()
            storage.delete(storage_path, None)
            return True
        except Exception as e:
            # Optionally log the error if logger is available
            print(f"Error deleting file from Firebase Storage: {e}")
            return False