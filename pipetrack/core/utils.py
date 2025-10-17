import json
from typing import Dict, Any


def safe_json_load(line: str) -> Dict[str, Any]:
    """
    Safely load a JSON string and return a dictionary.

    Returns an empty dictionary if parsing fails.
    """
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return {}
