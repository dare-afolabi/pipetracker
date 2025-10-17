import requests
from typing import Dict


class Verifier:
    """Validates traces against configured service endpoints."""

    def verify(self, service: str, id: str, endpoint: str) -> Dict[str, str]:
        """
        Verify a trace ID against a service endpoint.

        Args:
            service (str): Service name.
            id (str): Trace ID.
            endpoint (str): Verification endpoint URL.

        Returns:
            dict: JSON response from the service on failure.
        """
        try:
            response = requests.get(
                f"{endpoint}?service={service}&id={id}", timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {"status": "error"}
