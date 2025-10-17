from pipetrack.core.log_scanner import LogScanner


def test_scan_local(mocker):
    # Mock os.walk to simulate a directory containing one log file
    mocker.patch("os.walk", return_value=[("./logs", [], ["log.txt"])])

    # Initialize scanner with the mocked log source
    scanner = LogScanner(["./logs"])
    files = scanner.scan()

    # Assertions
    assert len(files) == 1
    assert files[0].endswith("log.txt")
