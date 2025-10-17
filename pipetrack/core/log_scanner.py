from pipetrack.core.plugin_loader import load_plugin
from typing import List


class LogScanner:
    """Scans and fetches log files from configured sources."""

    def __init__(self, log_sources: List[str]):
        self.log_sources = log_sources

    def scan(self) -> List[str]:
        """Scan and fetch log files from all sources."""
        files = []

        for source in self.log_sources:
            if source.startswith("s3://"):
                plugin_path = "pipetrack.plugins.s3_plugin.S3Plugin"
            elif source.startswith("gs://"):
                plugin_path = "pipetrack.plugins.gcs_plugin.GCSPlugin"
            elif source.startswith("kafka://"):
                plugin_path = "pipetrack.plugins.kafka_plugin.KafkaPlugin"
            elif source.startswith("datadog://"):
                plugin_path = "pipetrack.plugins.datadog_plugin.DatadogPlugin"
            else:
                plugin_path = "pipetrack.plugins.local_plugin.LocalPlugin"

            try:
                plugin = load_plugin(plugin_path)
                files.extend(plugin.fetch_logs(source))
            except Exception as e:
                print(f"Error loading {plugin_path} for {source}: {e}")

        return files
