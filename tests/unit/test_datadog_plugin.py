from pipetrack.plugins import datadog_plugin


def test_datadog_plugin_send(monkeypatch):
    class FakeLogsApi:
        def __init__(self, api_client):
            pass

        def submit_log(self, body):
            return {"status": "ok"}

    def fake_loader():
        class FakeConfig:
            pass

        class FakeApiClient:
            def __init__(self, configuration):
                self.configuration = configuration

            def __enter__(self):
                return self

            def __exit__(self, *a):
                pass

        return (
            FakeApiClient,
            FakeConfig,
            lambda api_client: FakeLogsApi(api_client),
        )

    # Patch the internal Datadog client loader
    monkeypatch.setattr(datadog_plugin, "_get_datadog_client", fake_loader)

    # Instantiate plugin and test send_log
    plugin = datadog_plugin.DatadogPlugin(api_key="fake")
    result = plugin.send_log({"msg": "hello"})

    # --- Assertions ---
    assert isinstance(result, dict)
    assert result["status"] == "ok"
