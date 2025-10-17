import pandas as pd
import json
from pipetrack.core.config_loader import ConfigLoader
from pipetrack.core.log_scanner import LogScanner
from pipetrack.core.pattern_matcher import PatternMatcher
from pipetrack.core.trace_builder import TraceBuilder


def test_full_trace(tmp_path, mocker):
    # --- 1. Create temporary config file ---
    config_path = tmp_path / "test.yaml"
    config_content = """\
log_sources:
  - ./logs
match_keys:
  - transaction_id
output:
  format: html
  path: ./output
verifier_endpoints: {}
security:
  encrypt_logs: false
"""
    config_path.write_text(config_content, encoding="utf-8")

    # --- 2. Create a sample log ---
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

    # --- 3. Mock os.walk for LogScanner ---
    mocker.patch("os.walk", return_value=[(str(log_dir), [], ["test.log"])])

    # --- 4. Load config and scan logs ---
    conf = ConfigLoader().load(str(config_path))
    scanner = LogScanner(conf.log_sources)
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

                # Use dictionary-based matching
                if matcher.match_dict(log_data, "TXN12345"):
                    matches.append(
                        {
                            "timestamp": log_data.get("timestamp"),
                            "service": log_data.get("service"),
                            "raw": line.strip(),
                        }
                    )

    # --- 5. Build trace ---
    df = TraceBuilder().build(matches)

    # --- 6. Assertions ---
    assert isinstance(df, pd.DataFrame), "TraceBuilder must return a DataFrame"
    assert not df.empty, "Expected non-empty DataFrame from TraceBuilder"
    assert "service" in df.columns
    assert df.iloc[0]["service"] == "test-service"
