from pipetracker.plugins.base import LogSourcePlugin
from pipetracker.core.security import Security
import tempfile
from typing import List, Optional, Any
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class S3Plugin(LogSourcePlugin):
    """AWS S3 plugin for fetching logs."""

    def __init__(self, security: Optional[Security] = None):
        """Initialize the S3Plugin with an optional security instance.

        Args:
            security (Optional[Security]):\
                Security instance for credential management.
        """
        self.s3: Optional[Any] = None  # Any due to incomplete boto3 type stubs
        self.security = security or Security()

    def _get_boto3_client(
        self,
    ) -> Any:  # Any due to incomplete boto3 type stubs
        """Lazily initialize and return a boto3 S3 client.

        Returns:
            Any: Boto3 S3 client instance.

        Raises:
            ValueError: If AWS credentials are not available.
        """
        import boto3

        access_key = self.security.get_plugin_secret(
            "aws_access_key", env_var="AWS_ACCESS_KEY_ID"
        )
        secret_key = self.security.get_plugin_secret(
            "aws_secret_key", env_var="AWS_SECRET_ACCESS_KEY"
        )
        if not access_key or not secret_key:
            raise ValueError("AWS access key and secret key are required.")
        return boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def upload(self, bucket: str, key: str, data: bytes) -> None:
        """Upload data to an S3 bucket.

        Args:
            bucket (str): The S3 bucket name.
            key (str): The object key.
            data (bytes): The data to upload.
        """
        if self.s3 is None:
            self.s3 = self._get_boto3_client()
        self.s3.put_object(Bucket=bucket, Key=key, Body=data)

    def download(self, bucket: str, key: str) -> bytes:
        """Download data from an S3 bucket.

        Args:
            bucket (str): The S3 bucket name.
            key (str): The object key.

        Returns:
            bytes: The downloaded data.

        Note:
            Due to incomplete boto3 type stubs, the return type is enforced
            at runtime but may require type: ignore for strict MyPy checking.
        """
        if self.s3 is None:
            self.s3 = self._get_boto3_client()
        resp = self.s3.get_object(Bucket=bucket, Key=key)
        return resp["Body"].read()  # type: ignore[no-any-return]

    def fetch_logs(
        self, source: str, max_files: int = 100, max_size_mb: float = 10.0
    ) -> List[str]:
        """Fetch log file paths from S3.

        Args:
            source (str): S3 URL (e.g., 's3://bucket/path').
            max_files (int): Maximum number of files to process (default: 100).
            max_size_mb (float): Maximum total log size in MB (default: 10.0).

        Returns:
            List[str]: List of temporary file paths containing downloaded logs.

        Raises:
            ValueError: If the source is not a valid S3 URL.
            Exception: If an error occurs during S3 operations.
        """
        if not source.startswith("s3://"):
            raise ValueError(f"Invalid S3 source: {source}")
        parsed = urlparse(source)
        bucket = parsed.netloc
        prefix = parsed.path.lstrip("/")
        if self.s3 is None:
            self.s3 = self._get_boto3_client()
        log_files: List[str] = []
        total_size_bytes: int = 0
        max_size_bytes: int = int(max_size_mb * 1024 * 1024)
        paginator = self.s3.get_paginator("list_objects_v2")
        try:
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                for obj in page.get("Contents", []):
                    if len(log_files) >= max_files:
                        logger.info(f"Reached max_files limit ({max_files})")
                        break
                    key = obj["Key"]
                    if key.lower().endswith((".log", ".txt")):
                        obj_size = obj["Size"]
                        if total_size_bytes + obj_size > max_size_bytes:
                            logger.info(
                                f"Reached max_size limit ({max_size_mb} MB)"
                            )
                            break
                        temp_path = tempfile.NamedTemporaryFile(
                            delete=False
                        ).name
                        self.s3.download_file(
                            Bucket=bucket, Key=key, Filename=temp_path
                        )
                        log_files.append(temp_path)
                        total_size_bytes += obj_size
                        logger.info(f"Downloaded S3 log: {key} to {temp_path}")
        except Exception as e:
            logger.error(f"Error fetching S3 logs from {source}: {e}")
            raise
        return log_files
