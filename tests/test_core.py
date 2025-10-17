from pipetrack.core.config_loader import ConfigLoader
from pipetrack.core.log_scanner import LogScanner
from pipetrack.core.pattern_matcher import PatternMatcher
from pipetrack.core.trace_builder import TraceBuilder


def test_core_pipeline(tmp_path, mocker):
    # Create temporary config file
    config_path = tmp_path / "test.yaml"
    with open(config_path, "w") as f:
        f.write(
            """
log_sources: ['./logs']
match_keys: ['id']
output: {format: html, path: ./output}
verifier_endpoints: {}
security: {encrypt_logs: false}
"""
        )

    # Create mock log file
    log_path = tmp_path / "logs" / "test.log"
    log_path.parent.mkdir()
    with open(log_path, "w") as f:
        f.write(
            '{"id": "123", "timestamp": "2025-10-14T00:00:00", '
            '"service": "A", "message": "test"}'
        )

    # Mock os.walk for LogScanner
    mocker.patch(
        "os.walk", return_value=[(str(log_path.parent), [], ["test.log"])]
    )

    # Run pipeline
    conf = ConfigLoader().load(str(config_path))
    scanner = LogScanner(conf.log_sources)
    files = scanner.scan()
    matcher = PatternMatcher(conf.match_keys)

    matches = []
    for file_path in files:
        with open(file_path) as fh:
            for line in fh:
                if matcher.match_line(line, "123"):
                    matches.append(
                        {
                            "timestamp": matcher.extract_timestamp(line),
                            "service": matcher.extract_service(line),
                            "raw": line.strip(),
                        }
                    )

    df = TraceBuilder().build(matches)
    assert not df.empty
    assert df.iloc[0]["service"] == "A"
