import os
import logging
from typing import List, Optional
from pipetracker.core.plugin_loader import load_plugin
from pipetracker.core.config_loader import Config

logger = logging.getLogger(__name__)


class LogScanner:
    """Scan configured log sources and return a list of log file paths."""

    def __init__(self, sources: List[str], config: Optional[Config] = None):
        self.sources = sources or []
        self.config = config

    def scan(self) -> List[str]:
        log_files: List[str] = []
        total_size_bytes = 0
        max_files = self.config.output.max_files if self.config else 100
        max_size_bytes = int(
            (self.config.output.max_size_mb * 1024 * 1024)
            if self.config
            else 10 * 1024 * 1024
        )

        for source in self.sources:
            if "://" in source:
                scheme, details = source.split("://", 1)
                plugin_module = f"pipetracker.plugins.{scheme}_plugin"
                plugin_class = f"{scheme.capitalize()}Plugin"
                plugin_path = f"{plugin_module}:{plugin_class}"
            else:
                plugin_path = "pipetracker.plugins.local_plugin:LocalPlugin"
                source = os.path.abspath(os.path.expanduser(source))

            try:
                plugin = load_plugin(plugin_path)
                fetched_files = plugin.fetch_logs(
                    source,
                    max_files=max_files,
                    max_size_mb=(
                        self.config.output.max_size_mb if self.config else 10.0
                    ),
                )
                for file_path in fetched_files:
                    if len(log_files) >= max_files:
                        logger.warning(
                            f"Reached max_files limit ({max_files})"
                        )
                        break
                    file_size = (
                        os.path.getsize(file_path)
                        if os.path.exists(file_path)
                        else 0
                    )
                    if total_size_bytes + file_size > max_size_bytes:
                        logger.warning(
                            f"Reached max_size limit\
                                  ({self.config.output.max_size_mb
                                    if self.config else 10.0} MB)"
                        )
                        break
                    log_files.append(file_path)
                    total_size_bytes += file_size
            except Exception as e:
                logger.error(
                    f"Failed to load or fetch from plugin for {source}: {e}"
                )
                continue

        if not log_files:
            raise ValueError("No log files found in configured sources.")
        return log_files
