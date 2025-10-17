import requests_mock


def test_verify():
    from pipetrack.core.verifier import Verifier

    verifier = Verifier()

    with requests_mock.Mocker() as m:
        m.get("https://example.com?service=A&id=1", json={"status": "ok"})
        result = verifier.verify("A", "1", "https://example.com")

    assert result == {"status": "ok"}
