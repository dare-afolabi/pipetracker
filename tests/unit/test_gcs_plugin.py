from pipetrack.plugins import gcs_plugin


def test_gcs_plugin_upload(monkeypatch):
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

    # Patch lazy loader
    monkeypatch.setattr(
        gcs_plugin, "_get_storage_client", lambda: (lambda: FakeClient())
    )

    plugin = gcs_plugin.GCSPlugin(bucket="fake-bucket")
    success = plugin.upload("blob.txt", "hello cloud")

    assert success is True
    assert uploaded["blob.txt"] == "hello cloud"
