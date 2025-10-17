from typing import Optional, Any


def _get_boto3_client(
    service_name: Optional[str] = None, **kwargs: Any
) -> Optional[Any]:
    try:
        import boto3

        if service_name:
            return boto3.client(service_name, **kwargs)
        return boto3.client
    except ImportError:
        return None


class S3Plugin:
    def __init__(self, bucket: str) -> None:
        self.client = _get_boto3_client("s3")
        if self.client is None:
            raise ImportError("boto3 is not installed. Cannot use S3Plugin.")
        self.bucket = bucket

    def upload(self, key: str, data: Any) -> Any:
        return (
            self.client.put_object(Bucket=self.bucket, Key=key, Body=data)
            if self.client is not None
            else None
        )
