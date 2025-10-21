from abc import ABC, abstractmethod
from typing import List


class LogSourcePlugin(ABC):
    @abstractmethod
    def fetch_logs(
        self, source: str, max_files: int = 100, max_size_mb: float = 10.0
    ) -> List[str]:
        """
        Return a list of file paths or log lines from the given source.

        Args:
            source (str): The source location (e.g., local path, S3 bucket).
            max_files (int): Maximum number of files to fetch.
            max_size_mb (float): Maximum total size of logs in MB.

        Returns:
            List[str]: List of log file paths or log lines.
        """
