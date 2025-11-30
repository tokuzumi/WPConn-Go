import aioboto3
import logging
from botocore.exceptions import ClientError
from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.session = aioboto3.Session()
        self.endpoint_url = settings.MINIO_ENDPOINT
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.use_ssl = settings.MINIO_USE_SSL

    async def upload_stream(self, file_stream, object_name: str, content_type: str):
        """
        Uploads a file stream to MinIO.
        """
        try:
            async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                use_ssl=self.use_ssl,
            ) as s3:
                await s3.upload_fileobj(
                    file_stream,
                    self.bucket_name,
                    object_name,
                    ExtraArgs={"ContentType": content_type}
                )
                logger.info(f"Successfully uploaded {object_name} to {self.bucket_name}")
                return f"{self.bucket_name}/{object_name}"
        except ClientError as e:
            logger.error(f"Failed to upload to MinIO: {e}")
            raise e

    async def get_stream(self, object_name: str):
        """
        Gets a file stream from MinIO.
        """
        try:
            async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                use_ssl=self.use_ssl,
            ) as s3:
                response = await s3.get_object(Bucket=self.bucket_name, Key=object_name)
                return response["Body"]
        except ClientError as e:
            logger.error(f"Failed to get object from MinIO: {e}")
            raise e
