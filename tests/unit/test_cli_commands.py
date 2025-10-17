from typer.testing import CliRunner
from pipetrack.cli.main import app


def test_cli_help():
    runner = CliRunner()
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0
    assert "Pipetrack" in res.output or "Usage" in res.output
