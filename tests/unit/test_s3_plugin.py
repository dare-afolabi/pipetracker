from pipetrack.plugins import s3_plugin


def test_s3_plugin_upload(monkeypatch):
    class FakeS3:
        def put_object(self, Bucket, Key, Body):
            return {"Bucket": Bucket, "Key": Key, "Body": Body}

    # Patch lazy loader to return FakeS3 client
    monkeypatch.setattr(
        s3_plugin, "_get_boto3_client", lambda: (lambda service: FakeS3())
    )

    plugin = s3_plugin.S3Plugin(bucket="fake-bucket")
    result = plugin.upload("file.txt", b"hello world")

    assert result["Bucket"] == "fake-bucket"
    assert result["Key"] == "file.txt"
    assert result["Body"] == b"hello world"
