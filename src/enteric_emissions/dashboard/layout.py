"""Dash layout builders."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_layout(properties: list[str]) -> dbc.Container:
    """Create the unified analytics + forecast layout."""
    return dbc.Container(
        [
            html.H1(
                "Milk Production and Carbon Emissions Analysis",
                className="text-center mt-4 mb-4 display-4 font-weight-bold",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    dbc.Label(
                                        "Select Property",
                                        html_for="property-dropdown",
                                        className="font-weight-bold",
                                    ),
                                    dcc.Dropdown(
                                        id="property-dropdown",
                                        options=[
                                            {"label": prop, "value": prop}
                                            for prop in properties
                                        ],
                                        value=properties[0] if properties else None,
                                        multi=False,
                                        clearable=False,
                                        style={"font-weight": "bold"},
                                    ),
                                ],
                                className="mb-4",
                            ),
                            html.Div(
                                [
                                    dbc.Label(
                                        "Select Period Range",
                                        className="font-weight-bold",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id="start-year",
                                                    clearable=False,
                                                    placeholder="Start Year",
                                                )
                                            ),
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id="start-month",
                                                    clearable=False,
                                                    placeholder="Start Month",
                                                )
                                            ),
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id="end-year",
                                                    clearable=False,
                                                    placeholder="End Year",
                                                )
                                            ),
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id="end-month",
                                                    clearable=False,
                                                    placeholder="End Month",
                                                )
                                            ),
                                        ]
                                    ),
                                ],
                                className="mb-4",
                            ),
                            dbc.Button(
                                "Generate Prediction",
                                id="open-prediction-modal",
                                color="primary",
                                className="mb-4",
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(html.Div(id="kpi-cards"), md=9),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="line-chart"), md=6),
                    dbc.Col(dcc.Graph(id="carbon-evolution-chart"), md=6),
                ],
                className="mb-4",
            ),
            dbc.Row([dbc.Col(dcc.Graph(id="co2-per-liter-chart"), md=12)]),
            dbc.Modal(
                [
                    dbc.ModalHeader("3-Month Forecast"),
                    dbc.ModalBody(
                        [
                            dcc.Graph(id="milk-prediction-bar-chart"),
                            dcc.Graph(id="methane-prediction-bar-chart"),
                        ]
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close", id="close-prediction-modal", className="ms-auto"
                        )
                    ),
                ],
                id="prediction-modal",
                size="lg",
            ),
        ],
        fluid=True,
        style={"padding": "20px"},
    )
