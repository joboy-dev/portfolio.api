import os, requests
from typing import List, Optional
from uuid import uuid4
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from sqlalchemy.orm import Session
from decouple import config

from api.utils.loggers import create_logger
from api.utils.settings import settings
from api.utils.mime_types import EXTENSION_TO_MIME_TYPES_MAPPING
from api.v1.models.file import File
from api.v1.schemas.file import FileBase
from api.v1.services.file import FileService


logger = create_logger(__name__)

class BackblazeService:

    @classmethod
    def __get_client(cls):
        if getattr(cls, '_b2_client', None) is None:
            cls._b2_client = boto3.client(
                's3',
                endpoint_url=config('B2_ENDPOINT'),
                aws_access_key_id=config('B2_KEY_ID'),
                aws_secret_access_key=config('B2_APPLICATION_KEY'),
                config=Config(signature_version='s3v4'),
            )
        return cls._b2_client


    @classmethod
    def __ensure_bucket_exists(cls, bucket_name: str):
        """Creates the bucket if it doesn't already exist.

        Note: unlike Minio, B2's S3-compatible API has no put_bucket_policy,
        so a bucket's public/private access is set on the B2 side (console or
        native API) at creation time, not here.
        """

        try:
            cls.__get_client().head_bucket(Bucket=bucket_name)
        except ClientError:
            cls.__get_client().create_bucket(Bucket=bucket_name)


    @classmethod
    def generate_presigned_url(
        cls,
        object_name: str,
        response_content_disposition: str = None,
        expires_in: int = 3600
    ):
        bucket_name = config("B2_BUCKET_NAME")
        params = {
            'Bucket': bucket_name,
            'Key': object_name,
        }
        if response_content_disposition:
            params['ResponseContentDisposition'] = response_content_disposition

        try:
            url = cls.__get_client().generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expires_in
            )
            return url
        except ClientError as client_error:
            logger.error(f'An error occured: {client_error}')


    @classmethod
    async def upload_to_backblaze(
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
        '''This function uploads a file to a bucket in backblaze b2'''

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

        app_name = config("APP_NAME")
        bucket_name = config("B2_BUCKET_NAME")
        filename = new_file.get('file_name')
        file_extension = filename.split('.')[-1].lower()
        content_type = EXTENSION_TO_MIME_TYPES_MAPPING[file_extension]
        destination = f"{app_name}/{model_name}/{model_id}/{filename}" if model_id else f"{app_name}/{model_name}/{filename}"  # file extension is already included in filename
        source_file = new_file.get('file_path')

        try:
            cls.__ensure_bucket_exists(bucket_name)

            # Upload file
            cls.__get_client().upload_file(
                Filename=source_file,
                Bucket=bucket_name,
                Key=destination,
                ExtraArgs={'ContentType': content_type}
            )

            preview_url = cls.generate_presigned_url(
                object_name=destination,
                response_content_disposition="inline"
            ).split('?')[0]
            
            print(preview_url)

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

        except ClientError as client_error:
            raise client_error


    @classmethod
    def delete_file_from_backblaze(cls, object_name: str):
        """This function deletes a file from a backblaze bucket

        Args:
            object_name (str): Name of the file to be deleted
        """

        bucket_name = config("B2_BUCKET_NAME")
        try:
            cls.__get_client().delete_object(Bucket=bucket_name, Key=object_name)
            return True
        except ClientError as client_error:
            print(f'An error occured: {client_error}')
            return False


    @classmethod
    def download_file_from_backblaze(cls, url: str):
        """This downloads a file from a backblaze url to a temporary folder

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
