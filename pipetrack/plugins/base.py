from abc import ABC, abstractmethod
from typing import List


class LogSourcePlugin(ABC):
    @abstractmethod
    def fetch_logs(self, source: str) -> List[str]:
        """
        Return a list of file paths or log lines from the given source.

        Args:
            source (str): The source location (e.g., local path, S3 bucket).

        Returns:
            List[str]: List of log file paths or log lines.
        """
