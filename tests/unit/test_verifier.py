import requests_mock


def test_verify():
    """Test the Verifier class's verify method to ensure it correctly \
        handles a mocked HTTP response."""
    from pipetracker.core.verifier import Verifier

    verifier = Verifier()
    with requests_mock.Mocker() as m:
        m.get("https://example.com?service=A&id=1", json={"status": "ok"})
        result = verifier.verify("A", "1", "https://example.com")
    assert result == {"status": "ok"}
