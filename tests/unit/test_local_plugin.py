from pipetracker.plugins.local_plugin import LocalPlugin


def test_local_plugin_reads_single_file(tmp_path):
    """
    Test the LocalPlugin's read method to ensure it correctly reads records \
        from a single log file.
    """
    f = tmp_path / "log.txt"
    f.write_text("id=123 foo=bar\nid=123 foo=baz\n")
    p = LocalPlugin(path=str(tmp_path))
    records = list(p.read())
    assert len(records) >= 1
    if isinstance(records[0], dict):
        assert "id" in records[0]
