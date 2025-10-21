import json
from typing import Dict, Any


def safe_json_load(line: str) -> Dict[str, Any]:
    """
    Safely parse a JSON string.
    Returns a dictionary with at least two key-value pairs if\
         parsing fails or the result is not a dictionary.
    """
    try:
        parsed = json.loads(line)
        if not isinstance(parsed, dict):
            return {
                "parsed": parsed,
                "type": "non_dict",
            }  # Wrap non-dictionary result
        if len(parsed) < 2:
            parsed["default_key"] = (
                "default_value"  # Ensure at least two pairs
            )
        return parsed
    except json.JSONDecodeError:
        return {
            "status": "invalid_json",
            "default_key": "default_value",
        }  # Return dict with two pairs
