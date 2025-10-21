from pipetracker.plugins.s3_plugin import S3Plugin
import boto3
from moto import mock_aws


class TestS3Plugin(S3Plugin):
    def fetch_logs(self, source, max_files=100, max_size_mb=10.0):
        return []


def test_s3_plugin_upload(monkeypatch):
    """Test the upload method of the S3Plugin using a mocked \
        boto3 client."""

    class FakeS3:
        def put_object(self, Bucket, Key, Body):
            return {"Bucket": Bucket, "Key": Key, "Body": Body}

    monkeypatch.setattr(
        TestS3Plugin, "_get_boto3_client", lambda self: FakeS3()
    )
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "fake_access_key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "fake_secret_key")
    plugin = TestS3Plugin()
    plugin.upload("my-bucket", "my-key", b"data")


def test_s3_plugin_integration():
    """Test the integration of S3Plugin's upload and download \
        methods using moto's mock_aws."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")
        plugin = TestS3Plugin()
        plugin.upload("test-bucket", "test.txt", b"hello world")
        content = plugin.download("test-bucket", "test.txt")
        assert content == b"hello world"
