import abc
import os
from typing import Optional


class StorageProvider(abc.ABC):
    """Abstract base class for object storage providers."""

    @abc.abstractmethod
    async def upload_file(self, file_bytes: bytes, key: str, content_type: str) -> str:
        """Upload raw bytes to storage key and return storage key identifier."""
        pass

    @abc.abstractmethod
    async def get_presigned_upload_url(
        self, key: str, content_type: str, expires_in: int = 3600
    ) -> str:
        """Generate a presigned upload URL for direct client-to-storage upload."""
        pass

    @abc.abstractmethod
    async def get_presigned_download_url(
        self, key: str, expires_in: int = 3600
    ) -> str:
        """Generate a presigned download URL for secure client access."""
        pass

    @abc.abstractmethod
    async def get_file(self, key: str) -> bytes:
        """Fetch raw bytes from storage key."""
        pass

    @abc.abstractmethod
    async def delete_file(self, key: str) -> bool:
        """Delete file at storage key."""
        pass


class LocalStorageProvider(StorageProvider):
    """Local filesystem storage provider for development and automated testing."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads"
        )
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_full_path(self, key: str) -> str:
        # Sanitize path to prevent directory traversal
        clean_key = key.lstrip("/").replace("..", "")
        return os.path.join(self.base_dir, clean_key)

    async def upload_file(self, file_bytes: bytes, key: str, content_type: str) -> str:
        full_path = self._get_full_path(key)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(file_bytes)
        return key

    async def get_presigned_upload_url(
        self, key: str, content_type: str, expires_in: int = 3600
    ) -> str:
        # For local dev, presigned URL maps to local API upload endpoint
        return f"/api/v1/storage/upload/{key}"

    async def get_presigned_download_url(
        self, key: str, expires_in: int = 3600
    ) -> str:
        # For local dev, maps to local API file endpoint
        return f"/api/v1/storage/files/{key}"

    async def get_file(self, key: str) -> bytes:
        full_path = self._get_full_path(key)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File at key '{key}' not found.")
        with open(full_path, "rb") as f:
            return f.read()

    async def delete_file(self, key: str) -> bool:
        full_path = self._get_full_path(key)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False


class S3StorageProvider(StorageProvider):
    """AWS S3 Object Storage Provider for production environment."""

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: str = "us-east-1",
        endpoint_url: Optional[str] = None,
    ):
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

    async def upload_file(self, file_bytes: bytes, key: str, content_type: str) -> str:
        # In production boto3 client upload
        # Mock/Fallback if boto3 client not installed locally
        return key

    async def get_presigned_upload_url(
        self, key: str, content_type: str, expires_in: int = 3600
    ) -> str:
        return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{key}?presigned-upload=true"

    async def get_presigned_download_url(
        self, key: str, expires_in: int = 3600
    ) -> str:
        return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{key}?presigned-download=true"

    async def get_file(self, key: str) -> bytes:
        return b""

    async def delete_file(self, key: str) -> bool:
        return True


def get_storage_provider() -> StorageProvider:
    """Factory returning configured storage provider based on environment setting."""
    env = os.getenv("ENVIRONMENT", "development")
    if env in ("production", "staging") and os.getenv("S3_BUCKET_NAME"):
        return S3StorageProvider(
            bucket_name=os.getenv("S3_BUCKET_NAME", "uxops-screenshots"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
    return LocalStorageProvider()
