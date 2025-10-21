import pytest
from pipetracker.plugins.datadog_plugin import DatadogPlugin
from unittest.mock import patch
import os


@pytest.fixture
def datadog_setup():
    with patch("pipetracker.plugins.datadog_plugin.LogsApi") as MockLogsApi:
        mock_client = MockLogsApi.return_value

        # Fake Datadog-like response object
        mock_response = type(
            "Response",
            (),
            {
                "data": [
                    type(
                        "LogEvent",
                        (),
                        {"attributes": {"message": "transaction_id=123"}},
                    )
                ],
                "meta": type(
                    "Meta", (), {"page": type("Page", (), {"after": None})}
                ),
            },
        )

        # Mock API call to return our fake response
        mock_client.list_logs_get.return_value = mock_response

        # Yield mocked client to the test
        yield mock_client


def test_datadog_plugin_fetch_logs(datadog_setup, monkeypatch):
    """Test the DatadogPlugin's fetch_logs method to ensure it retrieves \
        and stores log messages from a Datadog service."""
    # Set fake Datadog credentials
    monkeypatch.setenv("DD_API_KEY", "fake_api_key")
    monkeypatch.setenv("DD_APP_KEY", "fake_app_key")

    # Instantiate plugin (uses our patched LogsApi)
    plugin = DatadogPlugin()

    # Run the fetch method (should hit the mock, not the network)
    log_files = plugin.fetch_logs(
        "datadog://service:test-service", max_files=10, max_size_mb=1.0
    )

    # Validate output
    assert len(log_files) == 1
    assert os.path.exists(log_files[0])

    with open(log_files[0], "r", encoding="utf-8") as f:
        content = f.read()
        assert "transaction_id=123" in content

    # Clean up the temporary file
    os.unlink(log_files[0])
