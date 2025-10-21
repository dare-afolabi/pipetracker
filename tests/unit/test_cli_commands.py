from typer.testing import CliRunner
from pipetracker.cli.main import app


def test_cli_help():
    """Test the CLI help command to ensure it executes \
        successfully and displays expected content."""
    runner = CliRunner()
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0
    assert "Pipetracker" in res.output or "Usage" in res.output
