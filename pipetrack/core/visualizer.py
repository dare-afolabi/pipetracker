import pandas as pd
import networkx as nx
import plotly.graph_objects as go


class Visualizer:
    """Generate visualizations for trace data, both HTML and CLI-friendly."""

    def to_html(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Generate an interactive HTML graph visualization of the trace.

        Args:
            df (pd.DataFrame): Trace DataFrame with at least 'service' column.
            output_path (str): Path to save the HTML file.
        """
        G: nx.DiGraph = nx.DiGraph()
        if not df.empty and "service" in df.columns:
            for i in range(len(df) - 1):
                G.add_edge(df["service"].iloc[i], df["service"].iloc[i + 1])

        pos = nx.spring_layout(G)
        edge_x, edge_y = [], []

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=0.5, color="#888"),
            hoverinfo="none",
            mode="lines",
        )

        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            hoverinfo="text",
            marker=dict(showscale=True, colorscale="YlGnBu", size=10),
            text=list(G.nodes()),
        )

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
            ),
        )
        fig.write_html(output_path)

    def to_cli(self, df: pd.DataFrame) -> str:
        """Generate a CLI-friendly string representation of the trace."""
        if df.empty:
            return "No trace data found."
        return df[["timestamp", "service", "raw"]].to_string(index=False)
