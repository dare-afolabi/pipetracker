import pandas as pd
import typer
import logging
from typing import Optional
import types

logger = logging.getLogger(__name__)

nx: Optional[types.ModuleType]
go: Optional[types.ModuleType]

try:
    import networkx as _nx
    import plotly.graph_objects as _go

    nx, go = _nx, _go
except ImportError:
    nx, go = None, None


class Visualizer:
    """Generate CLI and HTML visualizations for traces."""

    def to_cli(self, df: pd.DataFrame) -> str:
        if df.empty:
            return "[INFO] No trace data to display."
        lines = []
        for _, row in df.iterrows():
            lines.append(
                f"[{row['timestamp']}] {row['service']}: {row['raw']}"
            )
        return "\n".join(lines)

    def to_html(self, df: pd.DataFrame, output_path: str) -> None:
        if df.empty:
            with open(output_path, "w") as fh:
                fh.write("<p>No trace data to display.</p>")
            return
        if nx is None or go is None:
            logger.warning(
                "networkx or plotly not installed - Skipping trace HTML."
            )
            typer.echo(self.to_cli(df))
            return
        G = nx.DiGraph()
        previous_node = None
        for idx, row in df.iterrows():
            node_label = f"{row['service']}<br>{row['timestamp']}"
            G.add_node(node_label, raw=row["raw"])
            if previous_node:
                G.add_edge(previous_node, node_label)
            previous_node = node_label
        pos = nx.spring_layout(G)
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1, color="#888"),
            hoverinfo="none",
            mode="lines",
        )
        node_x = []
        node_y = []
        text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            text.append(f"{node}<br>{G.nodes[node]['raw']}")
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=text,
            hoverinfo="text",
            marker=dict(size=20, color="#1f77b4"),
        )
        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(
            showlegend=False, margin=dict(l=20, r=20, t=20, b=20)
        )
        fig.write_html(output_path)
