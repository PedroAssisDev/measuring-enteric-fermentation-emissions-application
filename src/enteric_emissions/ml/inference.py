"""LSTM inference helpers preserving original one-step and horizon behaviours."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from keras.models import load_model

from enteric_emissions.config import get_scientific_config


@dataclass
class PropertyArtifacts:
    model_milk: Any
    model_methane: Any
    scaler_features: Any
    scaler_target_milk: Any
    scaler_target_methane: Any


def load_property_artifacts(model_dir: Path | str, property_name: str) -> PropertyArtifacts:
    """Load Keras models and scalers for one property."""
    base = Path(model_dir) / property_name
    return PropertyArtifacts(
        model_milk=load_model(base / f"best_model_milk_{property_name}.keras"),
        model_methane=load_model(base / f"best_model_methane_{property_name}.keras"),
        scaler_features=np.load(
            base / f"scaler_features_{property_name}.npy", allow_pickle=True
        ).item(),
        scaler_target_milk=np.load(
            base / f"scaler_target_milk_{property_name}.npy", allow_pickle=True
        ).item(),
        scaler_target_methane=np.load(
            base / f"scaler_target_methane_{property_name}.npy", allow_pickle=True
        ).item(),
    )


def predict_one_step(
    artifacts: PropertyArtifacts,
    features: pd.DataFrame,
) -> tuple[float, float]:
    """One-step forecast matching the offline plotting behaviour (last window)."""
    cfg = get_scientific_config()
    scaled = artifacts.scaler_features.transform(features[list(cfg.lstm_feature_columns)])
    window = scaled[-cfg.lstm_time_steps :].reshape(1, cfg.lstm_time_steps, -1)
    milk_scaled = artifacts.model_milk.predict(window, verbose=0)
    methane_scaled = artifacts.model_methane.predict(window, verbose=0)
    milk = artifacts.scaler_target_milk.inverse_transform(milk_scaled).flatten()[0]
    methane = artifacts.scaler_target_methane.inverse_transform(methane_scaled).flatten()[0]
    return float(milk), float(methane)


def predict_horizon(
    artifacts: PropertyArtifacts,
    features: pd.DataFrame,
    n_months: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Multi-step forecast preserving the original Dash autoregressive strategy.

    The rollout feeds the milk prediction (tiled across feature dimensions)
    into the next input window for both targets, matching the published UI.
    """
    cfg = get_scientific_config()
    horizon = cfg.forecast_horizon_months if n_months is None else n_months
    feature_frame = features[list(cfg.lstm_feature_columns)]
    scaled_features = artifacts.scaler_features.transform(feature_frame)
    input_seq = np.expand_dims(scaled_features[-cfg.lstm_time_steps :], axis=0)

    predictions_milk: list[float] = []
    predictions_methane: list[float] = []
    for _ in range(horizon):
        pred_milk = artifacts.model_milk.predict(input_seq, verbose=0)
        pred_methane = artifacts.model_methane.predict(input_seq, verbose=0)
        predictions_milk.append(float(pred_milk[0, 0]))
        predictions_methane.append(float(pred_methane[0, 0]))
        next_input = np.concatenate(
            (
                input_seq[:, 1:, :],
                np.repeat(pred_milk.reshape(1, 1, 1), repeats=input_seq.shape[2], axis=2),
            ),
            axis=1,
        )
        input_seq = next_input

    milk = artifacts.scaler_target_milk.inverse_transform(
        np.array(predictions_milk).reshape(-1, 1)
    ).flatten()
    methane = artifacts.scaler_target_methane.inverse_transform(
        np.array(predictions_methane).reshape(-1, 1)
    ).flatten()
    return milk, methane
