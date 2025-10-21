from pipetracker.plugins.base import LogSourcePlugin
from pipetracker.core.security import Security
import tempfile
import logging
from urllib.parse import urlparse
from typing import Optional, List
import os
from google.cloud import storage  # Import for type hints

logger = logging.getLogger(__name__)


class GCSPlugin(LogSourcePlugin):
    """Google Cloud Storage plugin for fetching logs."""

    def __init__(self, security: Optional[Security] = None) -> None:
        """Initialize the GCSPlugin with an optional security instance.

        Args:
            security (Optional[Security]): Security instance for credential \
                management.
        """
        self.client: Optional[storage.Client] = None
        self.security = security or Security()

    def _get_client(self) -> storage.Client:
        """Lazily initialize and return a GCS client.

        Returns:
            storage.Client: Configured GCS client instance.

        Raises:
            ValueError: If GCS credentials are not available.
        """
        from google.cloud import storage

        credentials_path = self.security.get_plugin_secret(
            "gcs_credentials",
            env_var="GOOGLE_APPLICATION_CREDENTIALS",
            file_path=".gcs_credentials",
        )
        if os.path.exists(credentials_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        return storage.Client()

    def upload(self, bucket_name: str, blob_name: str, data: bytes) -> None:
        """Upload data to a GCS bucket.

        Args:
            bucket_name (str): The GCS bucket name.
            blob_name (str): The blob name.
            data (bytes): The data to upload.
        """
        if self.client is None:
            self.client = self._get_client()
        if self.client is not None:  # Type safety check
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_string(data)

    def download(self, bucket_name: str, blob_name: str) -> bytes:
        """Download data from a GCS bucket.

        Args:
            bucket_name (str): The GCS bucket name.
            blob_name (str): The blob name.

        Returns:
            bytes: The downloaded data.

        Raises:
            RuntimeError: If the GCS client could not be initialized.

        Note:
            Due to incomplete google-cloud-storage type stubs, a type: \
                ignore is used.
        """
        if self.client is None:
            self.client = self._get_client()
        if self.client is not None:  # Type safety check
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            return blob.download_as_bytes()  # type: ignore[no-any-return]
        raise RuntimeError("Failed to initialize GCS client")

    def fetch_logs(
        self, source: str, max_files: int = 100, max_size_mb: float = 10.0
    ) -> List[str]:
        """Fetch log file paths from GCS.

        Args:
            source (str): GCS URL (e.g., 'gcs://bucket/path').
            max_files (int): Maximum number of files to process (default: 100).
            max_size_mb (float): Maximum total log size in MB (default: 10.0).

        Returns:
            List[str]: List of temporary file paths containing downloaded logs.

        Raises:
            ValueError: If the source is not a valid GCS URL.
        """
        if not source.startswith("gcs://"):
            raise ValueError(f"Invalid GCS source: {source}")
        parsed = urlparse(source)
        bucket_name = parsed.netloc
        prefix = parsed.path.lstrip("/")
        if self.client is None:
            self.client = self._get_client()
        log_files: List[str] = []
        total_size_bytes: int = 0
        max_size_bytes: int = int(max_size_mb * 1024 * 1024)
        if (
            self.client is None
        ):  # Handle case where client initialization fails
            logger.error("Failed to initialize GCS client")
            return log_files
        try:
            blobs = self.client.bucket(bucket_name).list_blobs(prefix=prefix)
            if not hasattr(blobs, "__iter__"):  # Ensure blobs is iterable
                logger.warning(
                    f"Unexpected response from list_blobs for {bucket_name}"
                )
                return log_files
            for blob in blobs:
                if len(log_files) >= max_files:
                    logger.info(f"Reached max_files limit ({max_files})")
                    break
                if blob.name.lower().endswith((".log", ".txt")):
                    blob_size = blob.size
                    if total_size_bytes + blob_size > max_size_bytes:
                        logger.info(
                            f"Reached max_size limit ({max_size_mb} MB)"
                        )
                        break
                    temp_path = tempfile.NamedTemporaryFile(delete=False).name
                    blob.download_to_filename(temp_path)
                    log_files.append(temp_path)
                    total_size_bytes += blob_size
                    logger.info(
                        f"Downloaded GCS log: {blob.name} to {temp_path}"
                    )
        except Exception as e:
            logger.error(f"Error fetching GCS logs from {source}: {e}")
            return []  # Return empty list on exception
        return log_files
