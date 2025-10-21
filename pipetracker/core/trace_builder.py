import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TraceBuilder:
    """Build trace DataFrames from a list of matched log entries."""

    def build(self, matches: list[Dict[str, Any]]) -> pd.DataFrame:
        if not matches:
            return pd.DataFrame(columns=["timestamp", "service", "raw"])
        df = pd.DataFrame(matches)
        df = df[["timestamp", "service", "raw"]]
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        if df["timestamp"].isna().any():
            logger.warning(
                "Some timestamps could not be parsed and were set to NaT"
            )
        df = df.sort_values(by="timestamp").reset_index(drop=True)
        return df
