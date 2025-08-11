from datetime import timedelta
import json, requests, os
from typing import List, Optional
import secrets
from uuid import uuid4
from minio import Minio
from minio.error import S3Error
from sqlalchemy.orm import Session

from api.utils.loggers import create_logger
from api.utils.settings import settings
from api.utils.mime_types import EXTENSION_TO_MIME_TYPES_MAPPING
from api.v1.models.file import File
from api.v1.schemas.file import FileBase
from api.v1.services.file import FileService
from decouple import config


logger = create_logger(__name__)

class MinioService:

    @classmethod
    def __init__(cls):
        cls.minio_client = Minio(
            endpoint=config('MINIO_HOST'),
            access_key=config('MINIO_ACCESS_KEY'),
            secret_key=config('MINIO_SECRET_KEY'),
            secure=True
        )

    
    @classmethod
    def __make_public(cls, bucket_name: str):
        """This function makes a bucket public"""

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                }
            ]
        }
        
        # Set bucket policy
        cls.minio_client.set_bucket_policy(bucket_name, json.dumps(policy))


    @classmethod
    def generate_presigned_url(
        cls, 
        object_name: str, 
        response_content_disposition: str = None
    ):
        bucket_name = config("APP_NAME")
        try:
            url = cls.minio_client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                response_headers={
                    "response-content-disposition": response_content_disposition
                } if response_content_disposition else None
            )
            return url
        except S3Error as s3_error:
            print(f'An error occured: {s3_error}')
            

    @classmethod
    async def upload_to_minio(
        cls,
        db: Session,
        file,
        model_name: str,
        allowed_extensions: List[str],
        file_label: str = None,
        model_id: Optional[str] = None,
        file_description: str = None,
        add_to_db: bool = False,
        delete_after_upload: bool = True
    ):
        '''This function uploads a file to a bucket bucket in minio'''
        
        # Create file in db
        new_file = await FileService.upload_file(
            db=db,
            payload=FileBase(
                file=file,
                model_id=model_id,
                model_name=model_name,
                label=file_label,
                description=file_description
            ),
            allowed_extensions=allowed_extensions,
            add_to_db=add_to_db,
        )
        
        if isinstance(new_file, File):
            new_file = new_file.to_dict()

        bucket_name = config("APP_NAME")
        filename = new_file.get('file_name')
        file_extension = filename.split('.')[-1].lower()
        content_type = EXTENSION_TO_MIME_TYPES_MAPPING[file_extension]
        destination = f"{model_name}/{model_id}/{filename}" if model_id else f"{model_name}/{filename}"  # file extensuion is already included in filename
        source_file = new_file.get('file_path')
        
        try:
            if not cls.minio_client.bucket_exists(bucket_name):
                cls.minio_client.make_bucket(bucket_name)
            
            cls.__make_public(bucket_name)

            # Upload file
            cls.minio_client.fput_object(
                bucket_name=bucket_name,
                object_name=destination,
                file_path=source_file,
                content_type=content_type
            )

            preview_url = cls.generate_presigned_url(
                object_name=destination,
                response_content_disposition="inline"
            ).split('?')[0]
            
            # Generate download URL (attachment content disposition)
            # download_url = cls.generate_presigned_url(
            #     object_name=destination,
            #     response_content_disposition=f"attachment; filename={destination}"
            # )

            if new_file.get('id'):
                # Update file url
                File.update(
                    db=db,
                    id=new_file.get('id'),
                    url=preview_url
                )
                
            if delete_after_upload:
                try:
                    os.remove(new_file.get('file_path'))
                    logger.info(f"Deleted file at {new_file.get('file_path')} after upload")
                except Exception as e:
                    logger.error(f"Error deleting file after upload: {e}")
                    
                return new_file, preview_url

        except S3Error as s3_error:
            raise s3_error

    
    @classmethod
    def delete_file_from_minio(cls, object_name: str):
        """This function deletes a file from a minio bucket

        Args:
            object_name (str): Name of the file to be deleted
        """

        bucket_name = config("APP_NAME")
        try:
            cls.minio_client.remove_object(bucket_name, object_name)
            return True
        except S3Error as s3_error:
            print(f'An error occured: {s3_error}')
            return False
    
    
    @classmethod
    def download_file_from_minio(cls, url: str):
        """This downloads a file from a minio url to a temporary folder

        Args:
            url (str): File url
        """

        try:
            # Get save file extension from url
            save_file_extension = url.split('.')[-1]

            # Configure save path to save file to temporary directory
            save_path = os.path.join(settings.TEMP_DIR, f'tmp-{str(uuid4().hex)}.{save_file_extension}')
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            return save_path
        
        except requests.RequestException as e:
            print(f"Error downloading large file: {e}")
