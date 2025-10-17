from pipetrack.plugins.base import LogSourcePlugin
import os
import json
from typing import Optional


class LocalPlugin(LogSourcePlugin):
    def __init__(self, path: Optional[str] = None):
        self.path = path

    def fetch_logs(self, source: str) -> list:
        logs = []
        for root, _, files in os.walk(source or self.path or "."):
            for f in files:
                if f.endswith(".log") or f.endswith(".txt"):
                    logs.append(os.path.join(root, f))
        return logs

    def read(self):
        """Yield parsed log entries from all files."""
        for file_path in self.fetch_logs(self.path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    parsed = self.parse_line(line.strip())
                    if parsed:
                        yield parsed

    def parse_line(self, line: str) -> dict:
        """Parse a line as JSON or fallback to key=value parsing."""
        if not line:
            return {}
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            try:
                return dict(pair.split("=", 1) for pair in line.split())
            except Exception:
                return {"raw": line}
