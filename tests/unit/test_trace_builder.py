import pandas as pd
from pipetracker.core.trace_builder import TraceBuilder


def test_build():
    """Test the TraceBuilder's build method to ensure it correctly constructs \
        a DataFrame from log matches."""
    matches = [{"timestamp": "2025-10-14T00:00:00", "service": "A", "raw": ""}]
    df = TraceBuilder().build(matches)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert set(["timestamp", "service", "raw"]).issubset(df.columns)
    assert df.iloc[0]["service"] == "A"
