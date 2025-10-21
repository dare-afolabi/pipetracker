import pytest
from pipetracker.plugins.s3_plugin import S3Plugin
from moto import mock_aws
import boto3
import os


@pytest.fixture
def s3_setup():
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")
        s3.put_object(
            Bucket="test-bucket",
            Key="logs/test.log",
            Body=b"transaction_id=123",
        )
        yield s3


def test_s3_plugin_fetch_logs(s3_setup, monkeypatch):
    """Test the S3Plugin's fetch_logs method to ensure it \
        retrieves and stores log files from an S3 bucket."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "fake_access_key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "fake_secret_key")
    plugin = S3Plugin()
    log_files = plugin.fetch_logs(
        "s3://test-bucket/logs/", max_files=10, max_size_mb=1.0
    )
    assert len(log_files) == 1
    assert os.path.exists(log_files[0])
    with open(log_files[0], "r", encoding="utf-8") as f:
        assert "transaction_id=123" in f.read()
    os.unlink(log_files[0])
