import pandas as pd


def test_to_cli():
    """Test the Visualizer's to_cli method to ensure it generates a \
        string output containing expected data."""
    from pipetracker.core.visualizer import Visualizer

    df = pd.DataFrame(
        [{"timestamp": "2025-10-14T00:00:00", "service": "A", "raw": "test"}]
    )

    output = Visualizer().to_cli(df)

    assert isinstance(output, str)
    assert "A" in output
