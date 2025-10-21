import re
import json
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PatternMatcher:
    """Match trace IDs in log lines or dictionaries\
         based on configured keys."""

    def __init__(self, keys: List[str]):
        self.keys = keys or []

    def match_line(self, line: str, trace_id: str) -> bool:
        try:
            for key in self.keys:
                pattern = re.compile(
                    rf"{re.escape(key)}\s*[:=]\s*{re.escape(trace_id)}"
                )
                if pattern.search(line):
                    return True
        except re.error as e:
            logger.error(
                f"Invalid regex pattern for trace_id '{trace_id}': {e}"
            )
            return False
        return False

    def match_dict(self, log_dict: Dict[str, Any], trace_id: str) -> bool:
        for key in self.keys:
            if key in log_dict and str(log_dict[key]) == trace_id:
                return True
        return False

    def extract_timestamp(self, line: str) -> str:
        iso_pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        match = iso_pattern.search(line)
        return match.group(0) if match else ""

    def extract_service(self, line: str) -> str:
        """Extract the service name from a log line\
             using regex or JSON parsing."""
        service_pattern = re.compile(r"service\s*[:=]\s*(\S+)")
        match = service_pattern.search(line)
        if match:
            return match.group(1)
        try:
            log_json = json.loads(line)
            if not isinstance(log_json, dict):
                return ""
            service = log_json.get("service", "")
            return str(service)  # Explicitly convert to string
        except json.JSONDecodeError:
            return ""
