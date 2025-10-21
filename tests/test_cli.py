from typer.testing import CliRunner
from pipetracker.cli.main import app

runner = CliRunner()


def test_cli_help():
    """Test the CLI help command to ensure it executes successfully and \
        displays expected options."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "trace" in result.output


def test_trace_command(tmp_path, mocker):
    """Test the CLI trace command with a valid configuration but no \
        matching log files."""
    config_path = tmp_path / "test.yaml"
    with open(config_path, "w") as f:
        f.write(
            """
log_sources: ['./logs']
match_keys: ['id']
output: {format: cli, path: ./output, max_files: 100, max_size_mb: 10}
verifier_endpoints: {}
security: {encrypt_logs: false}
"""
        )
    mocker.patch("os.walk", return_value=[])
    result = runner.invoke(app, ["trace", "123", "--config", str(config_path)])
    assert result.exit_code == 0
    assert "No matches found" in result.output
