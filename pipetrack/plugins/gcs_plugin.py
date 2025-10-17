from typing import Optional, Any


def _get_storage_client() -> Optional[Any]:
    try:
        from google.cloud import storage

        return storage.Client
    except ImportError:
        return None


class GCSPlugin:
    def __init__(self, bucket: str) -> None:
        Client = _get_storage_client()
        if Client is None:
            raise ImportError(
                "google-cloud-storage is not installed. Cannot use GCSPlugin."
            )

        self.client = Client()
        self.bucket = self.client.bucket(bucket)

    def upload(self, blob_name: str, data: Any) -> bool:
        """Upload data (as string or bytes) to GCS."""
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(data)
        return True
