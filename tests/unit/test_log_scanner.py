from pipetracker.core.log_scanner import LogScanner


def test_scan_local(mocker, tmp_path):
    """Test the LogScanner's scan method to ensure it correctly identifies \
        log files in a local directory."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    log_file = log_dir / "log.txt"
    log_file.write_text("dummy log content")
    scanner = LogScanner([str(log_dir)])
    files = scanner.scan()
    assert len(files) == 1
    assert files[0] == str(log_file)
