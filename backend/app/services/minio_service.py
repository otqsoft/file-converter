import io
import json
from datetime import timedelta
from minio import Minio
from ..config import settings


class MinioService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.public_client = Minio(
            settings.MINIO_PUBLIC_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        if not self.client.bucket_exists(settings.MINIO_BUCKET):
            self.client.make_bucket(settings.MINIO_BUCKET)
        self._set_public_policy()

    def _set_public_policy(self):
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{settings.MINIO_BUCKET}/*"],
                }
            ],
        }
        self.client.set_bucket_policy(
            settings.MINIO_BUCKET,
            json.dumps(policy),
        )

    def upload_file(self, object_name: str, file_data: bytes, content_type: str = "application/octet-stream") -> str:
        self.client.put_object(
            settings.MINIO_BUCKET,
            object_name,
            io.BytesIO(file_data),
            length=len(file_data),
            content_type=content_type,
        )
        return object_name

    def upload_file_stream(self, object_name: str, stream: io.BytesIO, length: int, content_type: str = "application/octet-stream") -> str:
        self.client.put_object(
            settings.MINIO_BUCKET,
            object_name,
            stream,
            length=length,
            content_type=content_type,
        )
        return object_name

    def download_file(self, object_name: str) -> io.BytesIO:
        response = self.client.get_object(settings.MINIO_BUCKET, object_name)
        data = io.BytesIO(response.read())
        response.close()
        response.release_conn()
        data.seek(0)
        return data

    def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        return self.public_client.presigned_get_object(
            settings.MINIO_BUCKET,
            object_name,
            expires=timedelta(seconds=expires),
        )

    def delete_file(self, object_name: str):
        self.client.remove_object(settings.MINIO_BUCKET, object_name)
