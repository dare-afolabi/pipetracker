from typing import List
from pipetrack.core.utils import safe_json_load


class PatternMatcher:
    """Matches log lines against keys & extracts structured fields."""

    def __init__(self, match_keys: List[str]):
        self.match_keys = match_keys

    def match_line(self, line: str, value: str) -> bool:
        """Check if the log line matches the given value on any match key."""
        data = safe_json_load(line)
        return any(data.get(key) == value for key in self.match_keys)

    def match_dict(self, data: dict, value: str) -> bool:
        """Check if dictionary matches the given value on any match key."""
        if not isinstance(data, dict):
            return False
        return any(data.get(key) == value for key in self.match_keys)

    def extract_timestamp(self, line: str) -> str:
        """Extract timestamp from a JSON log line."""
        data = safe_json_load(line)
        return str(data.get("timestamp", ""))

    def extract_service(self, line: str) -> str:
        """Extract service name from a JSON log line."""
        data = safe_json_load(line)
        return str(data.get("service", ""))
