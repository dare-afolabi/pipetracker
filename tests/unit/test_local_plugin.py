from pipetrack.plugins.local_plugin import LocalPlugin


def test_local_plugin_reads_single_file(tmp_path):
    # create a temp log file
    f = tmp_path / "log.txt"
    f.write_text("id=123 foo=bar\nid=123 foo=baz\n")

    p = LocalPlugin(path=str(tmp_path))
    records = list(p.read())  # or adjust to the LocalPlugin API
    # Assert basic expectations
    assert len(records) >= 1
    # If plugin returns lines as dicts, check keys
    if isinstance(records[0], dict):
        assert "id" in records[0]
