import typer
from pipetrack.cli.command.trace import trace
from pipetrack.cli.command.config import config
import logging.config
import os

conf = os.path.join(os.path.dirname(__file__), "..", "logging.conf")
if os.path.exists(conf):
    logging.config.fileConfig(conf, disable_existing_loggers=False)
logger = logging.getLogger("pipetrack")

app = typer.Typer(
    name="pipetrack",
    help="Pipetrack: A tool for tracing logs across distributed sources.",
)

app.command()(trace)
app.command()(config)


if __name__ == "__main__":
    app()
