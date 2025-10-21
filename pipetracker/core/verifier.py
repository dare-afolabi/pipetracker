import requests
from typing import Dict, Any


class Verifier:
    def verify(
        self, service: str, trace_id: str, endpoint: str
    ) -> Dict[str, Any]:
        """
        Verify a trace against a service endpoint.

        Args:
            service: The service name to verify.
            trace_id: The trace identifier.
            endpoint: The verification endpoint URL.

        Returns:
            Dict[str, Any]: The response from the endpoint,\
                 typically a dictionary.

        Raises:
            requests.RequestException: If the request fails or\
                 response is invalid.
        """
        url = f"{endpoint}?service={service}&id={trace_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise requests.RequestException(
                    f"Invalid response format: expected dict,\
                         got {type(data).__name__}"
                )
            return data  # Ensured to be Dict[str, Any]
        except requests.RequestException as e:
            return {"error": str(e)}  # Consistent with Dict[str, Any]
