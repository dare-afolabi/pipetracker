from pipetracker.plugins.base import LogSourcePlugin
from pipetracker.core.security import Security
import tempfile
import logging
from urllib.parse import urlparse
from typing import List, Optional, Dict, TypedDict, Union, Any
from datetime import datetime, timedelta

# Datadog imports with type: ignore for untyped external library
from datadog_api_client.v2 import ApiClient, Configuration
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem
from datadog_api_client.model_utils import unset

logger = logging.getLogger(__name__)


class LogEntry(TypedDict):
    """Type definition for log entries sent to Datadog."""

    message: str
    ddsource: Optional[str]
    ddtags: Optional[List[str]]
    hostname: Optional[str]
    service: Optional[str]


class DatadogPlugin(LogSourcePlugin):
    """Datadog plugin for fetching and sending logs."""

    def __init__(self, security: Optional[Security] = None) -> None:
        self.client: Optional[LogsApi] = None
        self.security = security or Security()

    def _get_client(self) -> LogsApi:
        """Initialize and return a Datadog LogsApi client."""
        if self.client is not None:
            return self.client

        api_key = self.security.get_plugin_secret(
            "datadog_api_key", env_var="DD_API_KEY"
        )
        app_key = self.security.get_plugin_secret(
            "datadog_app_key", env_var="DD_APP_KEY"
        )
        if (
            not api_key
            or not app_key
            or not isinstance(api_key, str)
            or not isinstance(app_key, str)
        ):
            raise ValueError("Valid Datadog API and app keys required.")

        configuration = Configuration()  # type: ignore[no-untyped-call]
        configuration.api_key["apiKeyAuth"] = api_key
        configuration.api_key["appKeyAuth"] = app_key

        self.client = LogsApi(
            ApiClient(configuration)
        )  # type: ignore[no-untyped-call]
        return self.client

    def __del__(self) -> None:
        """Clean up the Datadog client on object deletion."""
        if (
            self.client is not None
            and hasattr(self.client, "api_client")
            and self.client.api_client is not None
        ):
            self.client.api_client.close()

    def send_log(
        self, log: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> Dict[str, str]:
        """
        Send log entries to Datadog.

        Args:
            log: A single log entry (dict) or list of log entries.

        Returns:
            A dictionary indicating the status of the operation.

        Raises:
            ValueError: If log format is invalid or sending fails.
        """
        if isinstance(log, dict):
            logs = [log]
        elif isinstance(log, list):
            logs = log
        else:
            raise ValueError("log must be a dict or a list of dicts")

        if self.client is None:
            self.client = self._get_client()

        try:
            for entry in logs:
                if not entry.get("message"):
                    raise ValueError("Log message is required.")

                tags: List[str] = entry.get("ddtags", [])
                log_item = HTTPLogItem(message=entry["message"])
                log_entry: HTTPLog = HTTPLog(  # type: ignore[no-untyped-call]
                    value=[log_item],
                    message=entry["message"],
                    ddsource=entry.get("ddsource", "pipetracker"),
                    ddtags=",".join(tags) if tags else None,
                    hostname=entry.get("hostname"),
                    service=entry.get("service"),
                )
                self.client.submit_log(log_entry)

            return {"status": "ok"}
        except Exception as e:
            logger.error(f"Failed to send log to Datadog: {str(e)}")
            raise ValueError(f"Failed to send log to Datadog: {str(e)}")

    def fetch_logs(
        self, source: str, max_files: int = 100, max_size_mb: float = 10.0
    ) -> List[str]:
        """
        Fetch logs from Datadog and store them in a temporary file.

        Args:
            source: Datadog query URL starting with 'datadog://'.
            max_files: Maximum number of log lines to fetch.
            max_size_mb: Maximum size of logs in megabytes.

        Returns:
            A list containing the path to a temporary file with fetched logs.

        Raises:
            ValueError: If the source URL or query is invalid, or \
                fetching fails.
        """
        if not source.startswith("datadog://"):
            raise ValueError(f"Invalid Datadog source URL: {source}")

        query = urlparse(source).netloc + urlparse(source).path
        if not query:
            raise ValueError(f"Invalid query in Datadog source: {source}")

        if self.client is None:
            self.client = self._get_client()

        log_lines: List[str] = []
        cursor: Optional[str] = None
        max_size_bytes = int(max_size_mb * 1024 * 1024)
        total_size_bytes = 0

        try:
            while len(log_lines) < max_files:
                filter_from = datetime.utcnow() - timedelta(minutes=15)
                filter_to = datetime.utcnow()
                response = self.client.list_logs_get(
                    filter_query=query,
                    filter_from=filter_from,
                    filter_to=filter_to,
                    page_limit=1000,
                    page_cursor=cursor if cursor is not None else unset,
                )
                for log_event in response.data:
                    content = log_event.attributes.get("message", "") or str(
                        log_event.attributes
                    )
                    encoded_size = len(content.encode())
                    if total_size_bytes + encoded_size > max_size_bytes:
                        logger.info(
                            f"Reached max_size limit ({max_size_mb} MB)"
                        )
                        break
                    log_lines.append(content)
                    total_size_bytes += encoded_size

                cursor = (
                    getattr(response.meta.page, "after", None)
                    if hasattr(response.meta, "page")
                    else None
                )
                if not cursor:
                    break

        except Exception as e:
            logger.error(f"Error fetching Datadog logs: {str(e)}")
            raise ValueError(f"Failed to fetch logs from Datadog: {str(e)}")

        if not log_lines:
            logger.info(f"No logs fetched for query: {query}")
            return []

        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            for line in log_lines[:max_files]:
                f.write(line + "\n")
            temp_path = f.name

        logger.info(f"Fetched Datadog logs to {temp_path}")
        return [temp_path]
