import time


class PerformanceTracker:
    """Utility class for tracking performance metrics across events."""

    def __init__(self):
        self.start_times = {}

    def mark(self, event: str) -> None:
        """Record the start time for a given event."""
        self.start_times[event] = time.time()

    def duration(self, event: str) -> float:
        """Return the elapsed time (in seconds) since the event was marked."""
        start_time = self.start_times.get(event)
        if start_time is None:
            return 0.0
        return time.time() - start_time
