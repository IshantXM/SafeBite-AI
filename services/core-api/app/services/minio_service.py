import io
import logging
from typing import Optional
from minio import Minio
from minio.error import S3Error

from app.config import settings

logger = logging.getLogger("MinIOService")


class MinIOService:
    def __init__(self):
        try:
            self.client = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ROOT_USER,
                secret_key=settings.MINIO_ROOT_PASSWORD,
                secure=settings.MINIO_SECURE,
            )
            self._ensure_buckets()
        except Exception as e:
            logger.warning(f"MinIO client initialization error: {e}. Fallback to simulated storage.")
            self.client = None

    def _ensure_buckets(self):
        """Ensures all necessary S3 buckets exist."""
        if not self.client:
            return
        buckets = [settings.MINIO_BUCKET_INSPECTIONS, settings.MINIO_BUCKET_REPORTS]
        for bucket in buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    logger.info(f"Created MinIO bucket: {bucket}")
            except Exception as e:
                logger.error(f"Error ensuring bucket {bucket}: {e}")

    def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        file_bytes: bytes,
        content_type: str = "image/jpeg"
    ) -> str:
        """Uploads bytes to MinIO and returns accessible URL."""
        if not self.client:
            # Fallback simulated URL for local dev without running MinIO container
            return f"{settings.MINIO_PUBLIC_URL}/{bucket_name}/{object_name}"

        try:
            data_stream = io.BytesIO(file_bytes)
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=data_stream,
                length=len(file_bytes),
                content_type=content_type
            )
            return f"{settings.MINIO_PUBLIC_URL}/{bucket_name}/{object_name}"
        except S3Error as e:
            logger.error(f"MinIO upload error for {object_name}: {e}")
            raise RuntimeError(f"Storage upload failed: {e}")


minio_service = MinIOService()
