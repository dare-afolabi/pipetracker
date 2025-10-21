import time
from typing import Dict


class PerformanceTracker:
    """Utility class for tracking performance metrics across events."""

    def __init__(self) -> None:
        """Initialize the PerformanceTracker with\
             an empty dictionary of start times."""
        self.start_times: Dict[str, float] = {}

    def mark(self, event: str) -> None:
        """Record the start time for a given event.

        Args:
            event (str): The name of the event to mark.
        """
        self.start_times[event] = time.time()

    def duration(self, event: str) -> float:
        """Return the elapsed time (in seconds) since the event was marked.

        Args:
            event (str): The name of the event to measure.

        Returns:
            float: The elapsed time in seconds,\
                 or 0.0 if the event was not marked.
        """
        start_time = self.start_times.get(event)
        if start_time is None:
            return 0.0
        return time.time() - start_time
