import pandas as pd


def test_to_cli():
    from pipetrack.core.visualizer import Visualizer

    df = pd.DataFrame(
        [{"timestamp": "2025-10-14T00:00:00", "service": "A", "raw": "test"}]
    )

    output = Visualizer().to_cli(df)

    assert isinstance(output, str)
    assert "A" in output
