from typing import Optional, Any


def _get_datadog_client() -> Optional[tuple[Any, Any, Any]]:
    try:
        from datadog_api_client import ApiClient, Configuration
        from datadog_api_client.v2.api.logs_api import LogsApi

        return ApiClient, Configuration, LogsApi
    except ImportError:
        return None


class DatadogPlugin:
    def __init__(self, api_key: str) -> None:
        clients = _get_datadog_client()
        if clients is None:
            raise ImportError(
                "datadog-api-client is not installed. Cannot use DatadogPlugin"
            )

        ApiClient, Configuration, LogsApi = clients
        self.configuration = Configuration()
        self.api_client = ApiClient(self.configuration)
        self.api_instance = LogsApi(self.api_client)

    def send_log(self, body: Any) -> Any:
        """Send log data to Datadog."""
        return self.api_instance.submit_log(body=body)
