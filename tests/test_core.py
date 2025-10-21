import json
from pipetracker.core.config_loader import ConfigLoader
from pipetracker.core.log_scanner import LogScanner
from pipetracker.core.pattern_matcher import PatternMatcher
from pipetracker.core.trace_builder import TraceBuilder
from pandas import Timestamp


def test_core_pipeline(tmp_path, mocker):
    """
    Test the core pipeline for processing logs and building traces.
    """
    config_path = tmp_path / "test.yaml"
    config_content = f"""\
log_sources:
  - {tmp_path}/logs
match_keys:
  - id
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
    log_dir.mkdir()
    log_path = log_dir / "test.log"
    log_entry = {
        "id": "123",
        "timestamp": "2025-10-14T00:00:00",
        "service": "A",
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
                log_data = json.loads(line.strip())
                if matcher.match_dict(log_data, "123"):
                    matches.append(
                        {
                            "timestamp": log_data.get("timestamp"),
                            "service": log_data.get("service"),
                            "raw": line.strip(),
                        }
                    )
    df = TraceBuilder().build(matches)
    assert not df.empty
    assert df.iloc[0]["service"] == "A"
    assert df.iloc[0]["timestamp"] == Timestamp("2025-10-14T00:00:00")
