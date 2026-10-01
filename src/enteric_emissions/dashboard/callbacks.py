"""Dash callbacks for KPIs, charts, and 3-month LSTM forecasts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State

from enteric_emissions.config import get_paths, get_scientific_config
from enteric_emissions.dashboard.indicators import build_kpi_cards
from enteric_emissions.ml.inference import load_property_artifacts, predict_horizon


def _filter_period(
    df: pd.DataFrame,
    property_name: str,
    start_year: int,
    start_month: int,
    end_year: int,
    end_month: int,
) -> pd.DataFrame:
    start_period = pd.to_datetime(f"{start_year}-{start_month:02d}")
    end_period = pd.to_datetime(f"{end_year}-{end_month:02d}")
    return df[
        (df["Property"] == property_name)
        & (df["Period"] >= start_period)
        & (df["Period"] <= end_period)
    ].sort_values("Period")


def register_callbacks(app: Dash, df: pd.DataFrame) -> None:
    """Attach all interactive callbacks to ``app``."""
    cfg = get_scientific_config()
    paths = get_paths()
    models_dir = paths.models_dir

    @app.callback(
        Output("prediction-modal", "is_open"),
        [
            Input("open-prediction-modal", "n_clicks"),
            Input("close-prediction-modal", "n_clicks"),
        ],
        [State("prediction-modal", "is_open")],
    )
    def toggle_prediction_modal(n_open, n_close, is_open):
        if n_open or n_close:
            return not is_open
        return is_open

    @app.callback(
        [
            Output("start-year", "options"),
            Output("end-year", "options"),
            Output("start-year", "value"),
            Output("end-year", "value"),
        ],
        [Input("property-dropdown", "value")],
    )
    def update_year_options(selected_property):
        filtered = df[df["Property"] == selected_property]
        years = sorted(filtered["Year"].unique())
        options = [{"label": str(y), "value": int(y)} for y in years]
        start = int(years[0]) if years else None
        end = int(years[-1]) if years else None
        return options, options, start, end

    @app.callback(
        [
            Output("start-month", "options"),
            Output("end-month", "options"),
            Output("start-month", "value"),
            Output("end-month", "value"),
        ],
        [
            Input("property-dropdown", "value"),
            Input("start-year", "value"),
            Input("end-year", "value"),
        ],
    )
    def update_month_options(selected_property, start_year, end_year):
        filtered = df[df["Property"] == selected_property]
        start_opts, end_opts = [], []
        start_default = end_default = None
        if start_year:
            months = sorted(filtered[filtered["Year"] == start_year]["Month"].unique())
            start_opts = [{"label": str(m), "value": int(m)} for m in months]
            start_default = int(months[0]) if months else None
        if end_year:
            months = sorted(filtered[filtered["Year"] == end_year]["Month"].unique())
            end_opts = [{"label": str(m), "value": int(m)} for m in months]
            end_default = int(months[-1]) if months else None
        return start_opts, end_opts, start_default, end_default

    @app.callback(
        Output("kpi-cards", "children"),
        [
            Input("property-dropdown", "value"),
            Input("start-year", "value"),
            Input("start-month", "value"),
            Input("end-year", "value"),
            Input("end-month", "value"),
        ],
    )
    def update_kpis(selected_property, start_year, start_month, end_year, end_month):
        if not all([start_year, start_month, end_year, end_month]):
            return []
        dff = _filter_period(
            df, selected_property, start_year, start_month, end_year, end_month
        )
        return build_kpi_cards(dff)

    def _line_figure(dff: pd.DataFrame, y_col: str, title: str, y_title: str) -> go.Figure:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=dff["Period"], y=dff[y_col], mode="lines+markers", name=y_col)
        )
        fig.update_layout(
            title=f"<b>{title}</b>",
            title_x=0.5,
            xaxis_title="<b>Period</b>",
            yaxis_title=f"<b>{y_title}</b>",
            font=dict(family="Arial", size=14, color="black"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(tickangle=-45, showgrid=True, gridcolor="LightGray"),
            yaxis=dict(showgrid=True, gridcolor="LightGray"),
        )
        return fig

    @app.callback(
        Output("line-chart", "figure"),
        [
            Input("property-dropdown", "value"),
            Input("start-year", "value"),
            Input("start-month", "value"),
            Input("end-year", "value"),
            Input("end-month", "value"),
        ],
    )
    def update_line_chart(selected_property, start_year, start_month, end_year, end_month):
        if not all([start_year, start_month, end_year, end_month]):
            return go.Figure()
        dff = _filter_period(
            df, selected_property, start_year, start_month, end_year, end_month
        )
        return _line_figure(
            dff, "Milk_Production", "Milk Production Over Time", "Milk Production (liters)"
        )

    @app.callback(
        Output("carbon-evolution-chart", "figure"),
        [
            Input("property-dropdown", "value"),
            Input("start-year", "value"),
            Input("start-month", "value"),
            Input("end-year", "value"),
            Input("end-month", "value"),
        ],
    )
    def update_carbon_chart(selected_property, start_year, start_month, end_year, end_month):
        if not all([start_year, start_month, end_year, end_month]):
            return go.Figure()
        dff = _filter_period(
            df, selected_property, start_year, start_month, end_year, end_month
        )
        return _line_figure(
            dff, "enteric_tCO2e", "Carbon Emissions Over Time", "CO2 Emissions (tCO2e)"
        )

    @app.callback(
        Output("co2-per-liter-chart", "figure"),
        [
            Input("property-dropdown", "value"),
            Input("start-year", "value"),
            Input("start-month", "value"),
            Input("end-year", "value"),
            Input("end-month", "value"),
        ],
    )
    def update_co2_per_liter(selected_property, start_year, start_month, end_year, end_month):
        if not all([start_year, start_month, end_year, end_month]):
            return go.Figure()
        dff = _filter_period(
            df, selected_property, start_year, start_month, end_year, end_month
        ).copy()
        dff["CO2_per_Liter"] = dff["enteric_tCO2e"] / dff["Milk_Production"]
        return _line_figure(
            dff,
            "CO2_per_Liter",
            "Kg of CO2 per Liter of Milk Over Time",
            "CO2 per Liter (kgCO2e/L)",
        )

    @app.callback(
        [
            Output("milk-prediction-bar-chart", "figure"),
            Output("methane-prediction-bar-chart", "figure"),
        ],
        [
            Input("property-dropdown", "value"),
            Input("start-year", "value"),
            Input("start-month", "value"),
            Input("end-year", "value"),
            Input("end-month", "value"),
            Input("open-prediction-modal", "n_clicks"),
        ],
    )
    def update_prediction_graphs(
        selected_property, start_year, start_month, end_year, end_month, _n_clicks
    ):
        empty = go.Figure()
        if not all([start_year, start_month, end_year, end_month, selected_property]):
            return empty, empty
        if selected_property not in cfg.properties_with_pretrained_models:
            fig = go.Figure()
            fig.update_layout(
                title=f"No pretrained model for {selected_property}. "
                f"Available: {', '.join(cfg.properties_with_pretrained_models)}"
            )
            return fig, fig

        filtered = _filter_period(
            df, selected_property, start_year, start_month, end_year, end_month
        )
        if len(filtered) < cfg.lstm_time_steps:
            fig = go.Figure()
            fig.update_layout(title="Not enough rows for LSTM window")
            return fig, fig

        artifacts = load_property_artifacts(models_dir, selected_property)
        recent = filtered.tail(cfg.lstm_time_steps)
        features = recent[list(cfg.lstm_feature_columns)]
        pred_milk, pred_methane = predict_horizon(artifacts, features)

        forecast_periods = pd.date_range(
            recent["Period"].max(),
            periods=cfg.forecast_horizon_months + 1,
            freq=pd.offsets.MonthEnd(),
        )[1:].strftime("%Y-%m")
        actual_periods = filtered["Period"].dt.strftime("%Y-%m")

        milk_fig = go.Figure()
        milk_fig.add_trace(
            go.Bar(
                x=actual_periods,
                y=filtered["Milk_Production"],
                name="Real Milk Production",
                marker_color="#636EFA",
                opacity=0.8,
            )
        )
        milk_fig.add_trace(
            go.Bar(
                x=list(forecast_periods),
                y=pred_milk,
                name="Milk Production Forecast",
                marker_color="#EF553B",
                opacity=0.7,
            )
        )
        milk_fig.update_layout(
            title=f"<b>Milk Production - {selected_property}</b>",
            title_x=0.5,
            xaxis_title="<b>Period</b>",
            yaxis_title="<b>Liters</b>",
            barmode="group",
            plot_bgcolor="white",
            paper_bgcolor="white",
        )

        methane_fig = go.Figure()
        methane_fig.add_trace(
            go.Bar(
                x=actual_periods,
                y=filtered["enteric_tCO2e"],
                name="Real Methane Emissions",
                marker_color="#636EFA",
                opacity=0.8,
            )
        )
        methane_fig.add_trace(
            go.Bar(
                x=list(forecast_periods),
                y=pred_methane,
                name="Methane Emissions Forecast",
                marker_color="#EF553B",
                opacity=0.7,
            )
        )
        methane_fig.update_layout(
            title=f"<b>Methane Emissions - {selected_property}</b>",
            title_x=0.5,
            xaxis_title="<b>Period</b>",
            yaxis_title="<b>tCO2e</b>",
            barmode="group",
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        return milk_fig, methane_fig
