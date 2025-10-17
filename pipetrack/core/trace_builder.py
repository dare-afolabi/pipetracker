import pandas as pd


class TraceBuilder:
    """Constructs and sorts a DataFrame from matched log entries."""

    def build(self, matches: list[dict]) -> pd.DataFrame:
        """Build a sorted DataFrame from matched log entries."""
        df = pd.DataFrame(matches)
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df = df.sort_values("timestamp")
        return df
