"""Matplotlib forecast plots (one-step), ported from the research plotting module."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from enteric_emissions.config import get_scientific_config
from enteric_emissions.ml.inference import PropertyArtifacts, predict_one_step

logger = logging.getLogger(__name__)


def plot_property_data(
    data: pd.DataFrame,
    property_name: str,
    save_path: Path | str,
    artifacts: PropertyArtifacts,
) -> Path:
    """Plot historical series and one-step forecast for one property."""
    cfg = get_scientific_config()
    property_data = data[data["Property"] == property_name].copy()
    property_data["Period"] = pd.to_datetime(property_data["Period"])
    property_data = property_data.set_index("Period")

    features = property_data[list(cfg.lstm_feature_columns)]
    milk_pred, methane_pred = predict_one_step(artifacts, features)

    # Preserve original date construction (next month after last observation).
    future_periods = pd.date_range(
        property_data.index[-1], periods=2, freq=pd.offsets.MonthEnd()
    )[1:]
    milk_forecast_df = pd.DataFrame(
        {"Period": future_periods, "Milk_Production": [milk_pred]}
    ).set_index("Period")
    methane_forecast_df = pd.DataFrame(
        {"Period": future_periods, "enteric_tCO2e": [methane_pred]}
    ).set_index("Period")

    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(
        property_data.index,
        property_data["Milk_Production"],
        marker="o",
        color="blue",
        label="Milk Production",
    )
    plt.plot(
        milk_forecast_df.index,
        milk_forecast_df["Milk_Production"],
        marker="o",
        color="yellow",
        label="Milk Forecast",
    )
    plt.title(f"Property: {property_name} - Milk Production")
    plt.xlabel("Period")
    plt.ylabel("Milk Production (liters)")
    plt.grid(True)
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(
        property_data.index,
        property_data["enteric_tCO2e"],
        marker="o",
        color="blue",
        label="Methane Emissions",
    )
    plt.plot(
        methane_forecast_df.index,
        methane_forecast_df["enteric_tCO2e"],
        marker="o",
        color="yellow",
        label="Methane Forecast",
    )
    plt.title(f"Property: {property_name} - Methane Emissions")
    plt.xlabel("Period")
    plt.ylabel("Methane Emissions (tCO2e)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    out_dir = Path(save_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"property_{property_name}_plots.png"
    plt.savefig(out_file)
    plt.close()
    logger.info("Saved plot for %s to %s", property_name, out_file)
    return out_file


def plot_all_properties(
    data: pd.DataFrame,
    models: dict[str, Any],
    save_path: Path | str,
) -> None:
    """Generate plots for every property present in ``models``."""
    for property_name in models["milk"]:
        artifacts = PropertyArtifacts(
            model_milk=models["milk"][property_name],
            model_methane=models["methane"][property_name],
            scaler_features=models["scalers"][property_name]["features"],
            scaler_target_milk=models["scalers"][property_name]["target_milk"],
            scaler_target_methane=models["scalers"][property_name]["target_methane"],
        )
        plot_property_data(data, property_name, save_path, artifacts)
