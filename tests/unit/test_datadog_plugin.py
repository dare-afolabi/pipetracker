from typing import List, Dict, Any
from unittest.mock import MagicMock
import pytest
from pipetracker.plugins.datadog_plugin import DatadogPlugin, LogEntry
from pipetracker.core.security import Security


class MockResponse:
    def __init__(self):
        self.data = [
            MagicMock(attributes={"message": "test log 1"}),
            MagicMock(attributes={"message": "test log 2"}),
        ]
        self.meta = MagicMock(page=MagicMock(after=None))


@pytest.fixture
def mock_security(mocker):
    security = mocker.create_autospec(Security)
    security.get_plugin_secret.side_effect = lambda key, env_var: "fake_key"
    return security


def test_datadog_plugin_send_full_mock(mocker, mock_security):
    """Test send_log method with mocked Datadog API."""

    class FakeLogsApi:
        def __init__(self):
            self.submitted: List[Any] = []
            self.api_client = FakeApiClient()

        def submit_log(self, log: Any) -> Dict[str, str]:
            self.submitted.append(log)
            return {"status": "ok"}

        def list_logs_get(self, *args, **kwargs) -> MockResponse:
            return MockResponse()

    class FakeApiClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def close(self):
            pass

    # Mock DatadogPlugin dependencies
    mocker.patch("pipetracker.plugins.datadog_plugin.Configuration")
    mocker.patch("pipetracker.plugins.datadog_plugin.ApiClient")
    mocker.patch(
        "pipetracker.plugins.datadog_plugin.LogsApi",
        return_value=FakeLogsApi(),
    )
    mock_http_log = mocker.patch("pipetracker.plugins.datadog_plugin.HTTPLog")
    mocker.patch("pipetracker.plugins.datadog_plugin.HTTPLogItem")

    # Configure HTTPLog mock to return expected attributes
    mock_log_instance = MagicMock()
    mock_log_instance.message = "test"
    mock_log_instance.ddsource = "test_source"
    mock_log_instance.ddtags = "tag1,tag2"
    mock_log_instance.hostname = "test_host"
    mock_log_instance.service = "test_service"
    mock_http_log.return_value = mock_log_instance

    # Create plugin instance
    plugin = DatadogPlugin(security=mock_security)

    # Test send_log
    logs_to_send: List[LogEntry] = [
        {
            "message": "test",
            "ddsource": "test_source",
            "ddtags": ["tag1", "tag2"],
            "hostname": "test_host",
            "service": "test_service",
        }
    ]
    response = plugin.send_log(logs_to_send)

    # Assertions
    assert response == {"status": "ok"}
    assert len(plugin.client.submitted) == 1
    assert plugin.client.submitted[0].message == "test"
    assert plugin.client.submitted[0].ddsource == "test_source"
    assert plugin.client.submitted[0].ddtags == "tag1,tag2"
    assert plugin.client.submitted[0].hostname == "test_host"
    assert plugin.client.submitted[0].service == "test_service"

    # Verify HTTPLog was called with correct arguments
    mock_http_log.assert_called_once_with(
        value=mocker.ANY,  # HTTPLogItem mock
        message="test",
        ddsource="test_source",
        ddtags="tag1,tag2",
        hostname="test_host",
        service="test_service",
    )


def test_datadog_plugin_fetch_logs_mock(mocker, mock_security, tmp_path):
    """Test fetch_logs method with mocked Datadog API."""

    class FakeLogsApi:
        def __init__(self):
            self.api_client = FakeApiClient()

        def list_logs_get(self, *args, **kwargs) -> MockResponse:
            return MockResponse()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    class FakeApiClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def close(self):
            pass

    # Mock DatadogPlugin dependencies
    mocker.patch("pipetracker.plugins.datadog_plugin.Configuration")
    mocker.patch("pipetracker.plugins.datadog_plugin.ApiClient")
    mocker.patch(
        "pipetracker.plugins.datadog_plugin.LogsApi",
        return_value=FakeLogsApi(),
    )

    # Create plugin instance
    plugin = DatadogPlugin(security=mock_security)

    # Test fetch_logs
    source = "datadog://test-query"
    response = plugin.fetch_logs(source, max_files=10, max_size_mb=1.0)

    # Assertions
    assert len(response) == 1
    with open(response[0], "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 2
    assert lines[0].strip() == "test log 1"
    assert lines[1].strip() == "test log 2"
