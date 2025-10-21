import typer
from pipetracker.cli.command.trace import trace
from pipetracker.cli.command.config import config
import logging.config
import os

conf = os.path.join(os.path.dirname(__file__), "..", "logging.conf")
if os.path.exists(conf):
    logging.config.fileConfig(conf, disable_existing_loggers=False)
else:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
logger = logging.getLogger("pipetracker")

app = typer.Typer(
    name="pipetracker",
    help="Pipetracker: A tool for tracing logs across distributed sources.",
)

app.command()(trace)
app.command()(config)

if __name__ == "__main__":
    app()
