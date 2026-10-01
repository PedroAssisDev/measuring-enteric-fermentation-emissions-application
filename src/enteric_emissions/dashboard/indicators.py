"""KPI calculations for the decision-support dashboard."""

from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html


def compute_kpi_values(dff: pd.DataFrame) -> dict[str, float]:
    """Compute numeric KPIs from a filtered property dataframe."""
    total_milk = float(dff["Milk_Production"].sum())
    total_carbon = float(dff["enteric_tCO2e"].sum())
    area_sum = float(dff["Area_Used_for_Dairy_Activity"].sum())
    return {
        "total_milk_production": total_milk,
        "total_carbon_emissions": total_carbon,
        "carbon_per_liter": (total_carbon / total_milk) if total_milk else 0.0,
        "carbon_per_area": (total_carbon / area_sum) if area_sum else 0.0,
        "milk_per_area": (total_milk / area_sum) if area_sum else 0.0,
    }


def build_kpi_cards(dff: pd.DataFrame) -> Any:
    """Build Bootstrap KPI cards matching the original dashboard layout."""
    kpis = compute_kpi_values(dff)
    return dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader("Total Milk Production", className="font-weight-bold"),
                        dbc.CardBody(
                            f"{kpis['total_milk_production']:.2f} liters",
                            className="display-6 font-weight-bold",
                        ),
                    ],
                    className="shadow-sm",
                    style={"margin-bottom": "10px", "background-color": "#f8f9fa"},
                )
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader("Total CO2 Emissions", className="font-weight-bold"),
                        dbc.CardBody(
                            f"{kpis['total_carbon_emissions']:.2f} tCO2e",
                            className="display-6 font-weight-bold",
                        ),
                    ],
                    className="shadow-sm",
                    style={"margin-bottom": "10px", "background-color": "#f8f9fa"},
                )
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            "Kg of CO2 per Liter of Milk", className="font-weight-bold"
                        ),
                        dbc.CardBody(
                            f"{kpis['carbon_per_liter']:.4f} kgCO2e/L",
                            className="display-6 font-weight-bold",
                        ),
                    ],
                    className="shadow-sm",
                    style={"margin-bottom": "10px", "background-color": "#f8f9fa"},
                )
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader("Kg of CO2 per Area Used", className="font-weight-bold"),
                        dbc.CardBody(
                            f"{kpis['carbon_per_area']:.4f} kgCO2e/ha",
                            className="display-6 font-weight-bold",
                        ),
                    ],
                    className="shadow-sm",
                    style={"margin-bottom": "10px", "background-color": "#f8f9fa"},
                )
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            "Liters of Milk per Area Used", className="font-weight-bold"
                        ),
                        dbc.CardBody(
                            f"{kpis['milk_per_area']:.2f} L/ha",
                            className="display-6 font-weight-bold",
                        ),
                    ],
                    className="shadow-sm",
                    style={"margin-bottom": "10px", "background-color": "#f8f9fa"},
                )
            ),
        ],
        className="g-4",
    )


def calculate_indicators_as_text(df: pd.DataFrame) -> list[str]:
    """Textual indicators (legacy helper used by early dashboard drafts)."""
    total_milk_production = df["Milk_Production"].sum()
    total_carbon_emission = df["enteric_tCO2e"].sum()
    carbon_per_liter = total_carbon_emission / total_milk_production
    carbon_per_area = total_carbon_emission / df["Area_Used_for_Dairy_Activity"].sum()
    carbon_per_cow = total_carbon_emission / df["Number_of_Lactating_Cows"].sum()
    milk_per_area = total_milk_production / df["Area_Used_for_Dairy_Activity"].sum()
    milk_per_cow = total_milk_production / df["Number_of_Lactating_Cows"].sum()
    return [
        f"Total Milk Production: {total_milk_production:.2f} liters",
        f"Total CO2 Emissions: {total_carbon_emission:.2f} tCO2e",
        f"CO2 per Liter of Milk: {carbon_per_liter:.2f} kgCO2e",
        f"CO2 per Area: {carbon_per_area:.2f} kgCO2e/ha",
        f"CO2 per Lactating Cow: {carbon_per_cow:.2f} kgCO2e/cow",
        f"Milk per Area: {milk_per_area:.2f} liters/ha",
        f"Milk per Lactating Cow: {milk_per_cow:.2f} liters/cow",
    ]
