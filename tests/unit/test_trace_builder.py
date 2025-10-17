import pandas as pd
from pipetrack.core.trace_builder import TraceBuilder


def test_build():
    # Mock match data
    matches = [{"timestamp": "2025-10-14T00:00:00", "service": "A", "raw": ""}]

    # Run build
    df = TraceBuilder().build(matches)

    # Assertions
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert set(["timestamp", "service", "raw"]).issubset(df.columns)
    assert df.iloc[0]["service"] == "A"
