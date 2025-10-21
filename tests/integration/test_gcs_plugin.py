import pytest
from pipetracker.plugins.gcs_plugin import GCSPlugin
from unittest.mock import patch
import os


@pytest.fixture
def gcs_setup():
    with patch("google.cloud.storage.Client") as MockClient:
        mock_client = MockClient.return_value
        mock_bucket = mock_client.bucket.return_value
        mock_blob = mock_bucket.blob.return_value
        mock_blob.download_to_filename.side_effect = lambda path: open(
            path, "w"
        ).write("transaction_id=123")
        mock_blob.size = 123
        mock_bucket.list_blobs.return_value = [mock_blob]
        yield mock_client


def test_gcs_plugin_fetch_logs(gcs_setup, monkeypatch):
    """Test the GCSPlugin's fetch_logs method to ensure it retrieves \
        and stores log files from a GCS bucket."""
    monkeypatch.setenv(
        "GOOGLE_APPLICATION_CREDENTIALS", "/fake/credentials.json"
    )
    plugin = GCSPlugin()
    log_files = plugin.fetch_logs(
        "gcs://test-bucket/logs/", max_files=10, max_size_mb=1.0
    )
    assert len(log_files) == 1
    assert os.path.exists(log_files[0])
    with open(log_files[0], "r", encoding="utf-8") as f:
        assert "transaction_id=123" in f.read()
    os.unlink(log_files[0])
