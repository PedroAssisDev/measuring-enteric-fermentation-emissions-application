"""Dash application factory."""

from __future__ import annotations

from pathlib import Path

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash

from enteric_emissions.config import get_paths
from enteric_emissions.dashboard.callbacks import register_callbacks
from enteric_emissions.dashboard.layout import create_layout
from enteric_emissions.data.io import load_csv


def load_dashboard_dataframe(data_path: Path | None = None) -> pd.DataFrame:
    """Load enriched property data and derive Year/Month columns."""
    path = data_path or get_paths().enriched_data
    df = load_csv(path)
    df["Period"] = pd.to_datetime(df["Period"])
    df["Year"] = df["Period"].dt.year
    df["Month"] = df["Period"].dt.month
    return df


def create_app(data_path: Path | None = None) -> Dash:
    """Create the configured Dash app."""
    df = load_dashboard_dataframe(data_path)
    app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
    app.layout = create_layout(sorted(df["Property"].unique().tolist()))
    register_callbacks(app, df)
    return app


def run_dashboard(
    host: str = "127.0.0.1",
    port: int = 8050,
    debug: bool = True,
) -> None:
    """Run the dashboard development server."""
    app = create_app()
    app.run_server(host=host, port=port, debug=debug)
