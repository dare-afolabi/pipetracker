from pipetracker.plugins.base import LogSourcePlugin
import os
import json
import logging
from typing import Optional, Generator, List, Dict, Any


class LocalPlugin(LogSourcePlugin):
    def __init__(self, path: Optional[str] = None) -> None:
        self.path: str = path or "."

    def fetch_logs(
        self,
        source: Optional[str] = None,
        max_files: int = 100,
        max_size_mb: float = 10.0,
    ) -> List[str]:
        logs: List[str] = []
        source = source or self.path
        max_size_bytes = int(max_size_mb * 1024 * 1024)
        total_size_bytes = 0
        if not os.path.exists(source):
            logging.warning(
                f"Source path {source} does not exist.\
                     Using current directory."
            )
            source = os.getcwd()
        for root, _, files in os.walk(source):
            for f in files:
                if len(logs) >= max_files:
                    logging.info(f"Reached max_files limit ({max_files})")
                    break
                if f.endswith((".log", ".txt")):
                    file_path = os.path.join(root, f)
                    try:
                        file_size = os.path.getsize(file_path)
                        if total_size_bytes + file_size > max_size_bytes:
                            logging.info(
                                f"Reached max_size limit ({max_size_mb} MB)"
                            )
                            break
                        if os.access(file_path, os.R_OK):
                            logs.append(file_path)
                            total_size_bytes += file_size
                        else:
                            logging.warning(
                                f"Cannot read file {file_path}, skipping."
                            )
                    except OSError as e:
                        logging.warning(f"Error accessing {file_path}: {e}")
                        continue
        return logs

    def read(self) -> Generator[Dict[str, Any], None, None]:
        for file_path in self.fetch_logs(self.path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parsed = self.parse_line(line.strip())
                        if parsed:
                            yield parsed
            except (OSError, UnicodeDecodeError) as e:
                logging.warning(f"Failed to read {file_path}: {e}")
                continue

    def parse_line(self, line: str) -> Dict[str, Any]:
        if not line:
            return {
                "status": "empty",
                "value": None,
            }  # Return dict with two key-value pairs
        try:
            parsed = json.loads(line)
            if not isinstance(parsed, dict):
                return {
                    "parsed": parsed,
                    "type": "non_dict",
                }  # Ensure dict return
            if len(parsed) < 2:
                parsed["default_key"] = (
                    "default_value"  # Ensure at least two pairs
                )
            return parsed
        except json.JSONDecodeError:
            try:
                pairs = [
                    pair.split("=", 1) for pair in line.split() if "=" in pair
                ]
                result = dict(pairs)
                if len(result) < 2:
                    result["default_key"] = (
                        "default_value"  # Ensure at least two pairs
                    )
                return result
            except (ValueError, AttributeError):
                return {
                    "raw": line,
                    "default_key": "default_value",
                }  # Ensure two pairs
