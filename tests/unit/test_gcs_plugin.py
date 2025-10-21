from pipetracker.plugins import gcs_plugin


class TestGCSPlugin(gcs_plugin.GCSPlugin):
    """Test-specific subclass of GCSPlugin to override fetch_logs and \
        customize upload behavior for testing."""

    def fetch_logs(self, source, max_files=100, max_size_mb=10.0):
        return []

    def upload(self, bucket_name: str, blob_name: str, data: bytes) -> bool:
        if self.client is None:
            self.client = self._get_client()
        if self.client is not None:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_string(data)
            return True
        return False


def test_gcs_plugin_upload(monkeypatch):
    """Test the upload method of GCSPlugin using a mocked GCS client."""
    uploaded = {}

    class FakeBlob:
        def __init__(self, name):
            self.name = name

        def upload_from_string(self, data):
            uploaded[self.name] = data

    class FakeBucket:
        def blob(self, name):
            return FakeBlob(name)

    class FakeClient:
        def bucket(self, bucket):
            return FakeBucket()

    monkeypatch.setattr(
        gcs_plugin.GCSPlugin, "_get_client", lambda self: FakeClient()
    )
    monkeypatch.setenv(
        "GOOGLE_APPLICATION_CREDENTIALS", "/fake/credentials.json"
    )
    plugin = TestGCSPlugin()
    success = plugin.upload("my-bucket", "blob.txt", b"hello cloud")
    assert success is True
    assert uploaded["blob.txt"] == b"hello cloud"


def test_gcs_plugin_integration(monkeypatch):
    """Test the integration of GCSPlugin's upload and download \
        methods using a mocked GCS client."""
    uploaded = {}

    class FakeBlob:
        def upload_from_string(self, data):
            uploaded["data"] = data

        def download_as_bytes(self):
            return uploaded["data"]

    class FakeBucket:
        def blob(self, name):
            return FakeBlob()

    class FakeClient:
        def bucket(self, name):
            return FakeBucket()

    monkeypatch.setattr(
        gcs_plugin.GCSPlugin, "_get_client", lambda self: FakeClient()
    )
    monkeypatch.setenv(
        "GOOGLE_APPLICATION_CREDENTIALS", "/fake/credentials.json"
    )
    plugin = TestGCSPlugin()
    plugin.upload("bucket", "file.txt", b"data")
    assert plugin.download("bucket", "file.txt") == b"data"
