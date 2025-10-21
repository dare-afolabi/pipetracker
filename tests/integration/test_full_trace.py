import json
import os

import pandas as pd
from cryptography.fernet import Fernet
from pipetracker.core.config_loader import ConfigLoader
from pipetracker.core.log_scanner import LogScanner
from pipetracker.core.pattern_matcher import PatternMatcher
from pipetracker.core.trace_builder import TraceBuilder
from pipetracker.core.verifier import Verifier
from pipetracker.core.visualizer import Visualizer
import pytest


@pytest.fixture
def encrypted_log_setup(tmp_path, mocker):
    config_path = (
        tmp_path / "secure.yaml"
    )  # Using Path implicitly via tmp_path
    config_content = f"""\
log_sources:
  - {tmp_path}/logs
match_keys:
  - transaction_id
output:
  format: cli
  path: {tmp_path}/output
  max_files: 100
  max_size_mb: 10
verifier_endpoints: {{}}
security:
  encrypt_logs: true
"""
    config_path.write_text(config_content, encoding="utf-8")

    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "secure.log"

    # Generate a valid Fernet key for mocking
    valid_key = Fernet.generate_key()
    mocker.patch(
        "pipetracker.core.security.get_or_create_key",
        return_value=valid_key,
    )

    from pipetracker.core.security import Security

    security = Security(encrypt_logs=True)
    original_data = (
        '{"transaction_id": "SEC123", "timestamp": "2025-10-15T00:00:00", '
        '"service": "secure-service", "message": "sensitive"}'
    )
    encrypted_line = security.encrypt_log(original_data)
    log_path.write_text(encrypted_line + "\n", encoding="utf-8")

    yield config_path, log_dir, log_path, security


def test_full_trace(tmp_path, mocker):
    """Test the full trace pipeline with unencrypted logs, including \
        scanning, matching, building, visualization, and verification."""
    config_path = tmp_path / "test.yaml"  # Using Path implicitly via tmp_path
    config_content = f"""\
log_sources:
  - {tmp_path}/logs
match_keys:
  - transaction_id
output:
  format: html
  path: {tmp_path}/output
  max_files: 100
  max_size_mb: 10
verifier_endpoints: {{}}
security:
  encrypt_logs: false
"""
    config_path.write_text(config_content, encoding="utf-8")
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "test.log"
    log_entry = {
        "transaction_id": "TXN12345",
        "timestamp": "2025-10-14T00:00:00",
        "service": "test-service",
        "message": "test",
    }
    log_path.write_text(f"{json.dumps(log_entry)}\n", encoding="utf-8")
    mocker.patch("os.walk", return_value=[(str(log_dir), [], ["test.log"])])
    conf = ConfigLoader().load(str(config_path))
    scanner = LogScanner(conf.log_sources, config=conf)
    files = scanner.scan()
    matcher = PatternMatcher(conf.match_keys)
    matches = []
    for file_path in files:
        with open(file_path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    log_data = json.loads(line.strip())
                except json.JSONDecodeError:
                    log_data = {"raw": line.strip()}
                if matcher.match_dict(log_data, "TXN12345"):
                    matches.append(
                        {
                            "timestamp": log_data.get("timestamp"),
                            "service": log_data.get("service"),
                            "raw": line.strip(),
                        }
                    )
    df = TraceBuilder().build(matches)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "service" in df.columns
    assert df.iloc[0]["service"] == "test-service"

    # Additional coverage: visualize
    visualizer = Visualizer()
    output_path = tmp_path / "output" / "trace_TXN12345.html"
    os.makedirs(output_path.parent, exist_ok=True)
    visualizer.to_html(df, str(output_path))
    assert output_path.exists()

    # Additional coverage: verifier (empty endpoints)
    verifier = Verifier()
    for service in df["service"].unique():
        if service in conf.verifier_endpoints:
            result = verifier.verify(
                service, "TXN12345", conf.verifier_endpoints[service]
            )
            assert result  # Would fail if endpoint present, but empty here


def test_full_trace_with_security(encrypted_log_setup, mocker):
    """Test the full trace pipeline with encrypted logs, including \
        decryption and PII masking."""
    config_path, log_dir, log_path, security = encrypted_log_setup
    mocker.patch("os.walk", return_value=[(str(log_dir), [], ["secure.log"])])

    conf = ConfigLoader().load(str(config_path))
    scanner = LogScanner(conf.log_sources, config=conf)
    files = scanner.scan()
    matcher = PatternMatcher(conf.match_keys)
    matches = []

    for file_path in files:
        with open(file_path, encoding="utf-8") as fh:
            for line in fh:
                decrypted = security.decrypt_log(line.strip())
                # Debugging: Print decrypted and processed lines
                print(f"Decrypted: {decrypted}")
                processed = security.mask_pii(decrypted)
                print(f"Processed: {processed}")
                try:
                    # Parse JSON to use match_dict instead of match_line
                    processed_data = json.loads(processed)
                    if matcher.match_dict(processed_data, "SEC123"):
                        matches.append(
                            {
                                "timestamp": processed_data.get("timestamp"),
                                "service": processed_data.get("service"),
                                "raw": processed.strip(),
                            }
                        )
                    else:
                        print(f"No match for 'SEC123' in: {processed_data}")
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON: {processed}")
                    if matcher.match_line(processed, "SEC123"):
                        matches.append(
                            {
                                "timestamp": matcher.extract_timestamp(
                                    processed
                                ),
                                "service": matcher.extract_service(processed),
                                "raw": processed.strip(),
                            }
                        )
                    else:
                        print(f"No match for 'SEC123' in: {processed}")

    assert (
        len(matches) == 1
    ), f"Expected 1 match, got {len(matches)}. Matches: {matches}"
