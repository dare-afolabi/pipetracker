from fastapi.testclient import TestClient
from pipetracker.api.main import app
from unittest.mock import patch, MagicMock
import tempfile
import os
from pipetracker.core.security import Security

client = TestClient(app)


def test_health_check():
    """Verify the health check endpoint returns a successful response."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "pipetracker"


@patch("pipetracker.api.routes.trace.ConfigLoader")
@patch("pipetracker.api.routes.trace.LogScanner")
@patch("pipetracker.api.routes.trace.PatternMatcher")
@patch("pipetracker.api.routes.trace.TraceBuilder")
def test_get_trace_success(
    mock_builder, mock_matcher, mock_scanner, mock_loader
):
    """Test successful trace retrieval with valid configuration and data."""
    # Mock config loading to return a pre-configured object
    mock_conf = MagicMock()
    mock_conf.security.encrypt_logs = False
    mock_conf.log_sources = [os.path.dirname(tempfile.gettempdir())]
    mock_conf.match_keys = ["transaction_id"]
    mock_loader.return_value.load.return_value = mock_conf

    # Mock scanner with a temporary file
    temp_dir = tempfile.gettempdir()
    temp_file = tempfile.NamedTemporaryFile(
        dir=temp_dir, delete=False, suffix=".log"
    )
    temp_file.write(
        b'{"timestamp": "2025-10-21T00:38:00", "service": "A", '
        b'"transaction_id": "123", "message": "test"}'
    )
    temp_file.close()
    mock_scanner.return_value.scan.return_value = [temp_file.name]
    print(f"Mocked file path: {temp_file.name}")

    # Mock matcher
    mock_match_instance = mock_matcher.return_value
    mock_match_instance.match_line.return_value = True
    mock_match_instance.extract_timestamp.return_value = "2025-10-21T00:38:00"
    mock_match_instance.extract_service.return_value = "A"

    # Mock builder
    mock_build_instance = mock_builder.return_value
    mock_df = mock_build_instance.build.return_value
    mock_df.to_dict.return_value = [
        {"timestamp": "2025-10-21T00:38:00", "service": "A", "raw": "test"}
    ]
    mock_df.rename.return_value = mock_df

    # Explicitly pass config_path
    response = client.get("/trace/123?config_path=test_config.yaml")
    print(f"Response status: {response.status_code}, Body: {response.text}")

    # Verify mocks were called
    print(f"ConfigLoader.load called: {mock_loader.return_value.load.called}")
    print(
        f"ConfigLoader.load call args: \
            {mock_loader.return_value.load.call_args}"
    )
    assert (
        mock_loader.return_value.load.called
    ), "ConfigLoader.load was not called"
    assert (
        mock_scanner.return_value.scan.called
    ), "LogScanner.scan was not called"
    assert (
        mock_matcher.return_value.match_line.called
    ), "PatternMatcher.match_line was not called"
    assert (
        mock_builder.return_value.build.called
    ), "TraceBuilder.build was not called"

    assert response.status_code == 200
    json_resp = response.json()
    assert len(json_resp) == 1
    assert json_resp[0]["timestamp"] == "2025-10-21T00:38:00"
    assert json_resp[0]["service"] == "A"

    # Cleanup
    try:
        os.unlink(temp_file.name)
    except (PermissionError, OSError) as e:
        print(f"Failed to delete temporary file {temp_file.name}: {e}")


@patch("pipetracker.api.routes.trace.ConfigLoader")
def test_get_trace_file_not_found(mock_loader):
    """Test handling of non-existent configuration file."""
    mock_loader.return_value.load.side_effect = FileNotFoundError(
        "Config not found"
    )
    response = client.get("/trace/123?config_path=invalid.yaml")
    assert response.status_code == 404
    assert "Config not found" in response.json()["detail"]


@patch("pipetracker.api.routes.trace.ConfigLoader")
@patch("pipetracker.api.routes.trace.LogScanner")
def test_get_trace_invalid_config(mock_scanner, mock_loader):
    """Test handling of invalid configuration format."""
    mock_loader.return_value.load.side_effect = ValueError(
        "Invalid config format"
    )
    response = client.get("/trace/123")
    assert response.status_code == 400
    assert "Invalid config format" in response.json()["detail"]


@patch("pipetracker.api.routes.trace.ConfigLoader")
@patch("pipetracker.api.routes.trace.LogScanner")
@patch("pipetracker.api.routes.trace.PatternMatcher")
def test_get_trace_io_error(mock_matcher, mock_scanner, mock_loader):
    """Test handling of IO errors during file processing."""
    mock_conf = mock_loader.return_value.load.return_value
    mock_conf.security.encrypt_logs = False
    mock_conf.log_sources = ["./logs"]
    mock_conf.match_keys = ["transaction_id"]

    mock_scanner.return_value.scan.return_value = ["non_existent_file"]

    response = client.get("/trace/123")
    assert response.status_code == 500
    assert "Error processing" in response.json()["detail"]


@patch("pipetracker.api.routes.trace.ConfigLoader")
@patch("pipetracker.api.routes.trace.LogScanner")
@patch("pipetracker.api.routes.trace.PatternMatcher")
@patch("pipetracker.api.routes.trace.TraceBuilder")
def test_get_trace_no_matches(
    mock_builder, mock_matcher, mock_scanner, mock_loader
):
    """Test handling of no matches for the trace ID."""
    mock_conf = mock_loader.return_value.load.return_value
    mock_conf.security.encrypt_logs = False
    mock_conf.log_sources = ["./logs"]
    mock_conf.match_keys = ["transaction_id"]

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(b"no match data")
    temp_file.close()
    mock_scanner.return_value.scan.return_value = [temp_file.name]

    mock_match_instance = mock_matcher.return_value
    mock_match_instance.match_line.return_value = False

    response = client.get("/trace/123")
    assert response.status_code == 200
    assert response.json() == []

    # Cleanup
    try:
        os.unlink(temp_file.name)
    except (PermissionError, OSError) as e:
        print(f"Failed to delete temporary file {temp_file.name}: {e}")


@patch("pipetracker.api.routes.trace.ConfigLoader")
@patch("pipetracker.api.routes.trace.LogScanner")
@patch("pipetracker.api.routes.trace.PatternMatcher")
@patch("pipetracker.api.routes.trace.TraceBuilder")
def test_get_trace_encrypted_success(
    mock_builder, mock_matcher, mock_scanner, mock_loader
):
    """Test successful trace retrieval with encrypted logs."""
    # Mock config loading
    mock_conf = mock_loader.return_value.load.return_value
    mock_conf.security.encrypt_logs = True
    mock_conf.log_sources = [os.path.dirname(tempfile.gettempdir())]
    mock_conf.match_keys = ["transaction_id"]

    # Mock scanner with encrypted data
    # Mock scanner with encrypted data
    temp_dir = tempfile.gettempdir()
    temp_file = tempfile.NamedTemporaryFile(
        dir=temp_dir, delete=False, suffix=".log"
    )
    security = Security(encrypt_logs=True)
    encrypted_data = security.encrypt_log(
        '{"transaction_id": "ENC123", "timestamp": "2025-10-21T00:38:00", '
        '"service": "B", "message": "encrypted"}'
    )
    temp_file.write(encrypted_data.encode())
    temp_file.close()
    mock_scanner.return_value.scan.return_value = [temp_file.name]
    print(f"Mocked encrypted file path: {temp_file.name}")

    # Mock matcher
    mock_match_instance = mock_matcher.return_value
    mock_match_instance.match_line.return_value = True
    mock_match_instance.extract_timestamp.return_value = "2025-10-21T00:38:00"
    mock_match_instance.extract_service.return_value = "B"

    # Mock builder
    mock_build_instance = mock_builder.return_value
    mock_df = mock_build_instance.build.return_value
    mock_df.to_dict.return_value = [
        {
            "timestamp": "2025-10-21T00:38:00",
            "service": "B",
            "raw": "encrypted",
        }
    ]
    mock_df.rename.return_value = mock_df

    response = client.get("/trace/ENC123")
    print(f"Response status: {response.status_code}, Body: {response.text}")

    assert response.status_code == 200
    json_resp = response.json()
    assert len(json_resp) == 1
    assert json_resp[0]["timestamp"] == "2025-10-21T00:38:00"
    assert json_resp[0]["service"] == "B"

    # Cleanup
    try:
        os.unlink(temp_file.name)
    except (PermissionError, OSError) as e:
        print(f"Failed to delete temporary file {temp_file.name}: {e}")


@patch("pipetracker.api.routes.trace.ConfigLoader")
@patch("pipetracker.api.routes.trace.LogScanner")
def test_get_trace_runtime_error(mock_scanner, mock_loader):
    """Test handling of unexpected runtime errors during trace processing."""
    mock_loader.return_value.load.side_effect = RuntimeError(
        "Unexpected error"
    )
    response = client.get("/trace/123")
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]
