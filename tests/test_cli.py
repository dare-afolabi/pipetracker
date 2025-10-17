from typer.testing import CliRunner
from pipetrack.cli.main import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "trace" in result.output


def test_trace_command(tmp_path, mocker):
    # Create temporary config file
    config_path = tmp_path / "test.yaml"
    with open(config_path, "w") as f:
        f.write(
            """
log_sources: ['./logs']
match_keys: ['id']
output: {format: cli, path: ./output}
verifier_endpoints: {}
security: {encrypt_logs: false}
"""
        )
    # Mock os.walk to simulate empty log directory
    mocker.patch("os.walk", return_value=[])

    # Invoke trace command
    result = runner.invoke(app, ["trace", "123", "--config", str(config_path)])
    assert result.exit_code == 0
    assert "No trace data found" in result.output
