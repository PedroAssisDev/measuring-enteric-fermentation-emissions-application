"""Per-property LSTM training and hyperparameter selection.

Preserves the original architecture and selection criterion (RMSE on scaled
test targets) from the research implementation.
"""

from __future__ import annotations

import logging
import os
from itertools import product
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
from keras.layers import Dense, LSTM
from keras.models import Sequential
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler

from enteric_emissions.config import get_scientific_config
from enteric_emissions.ml.sequences import create_sequences

logger = logging.getLogger(__name__)


def build_and_train_lstm(
    x_train: np.ndarray,
    y_train: np.ndarray,
    lstm_units: int = 50,
    epochs: int = 50,
    batch_size: int = 16,
    validation_split: float | None = None,
) -> Sequential:
    """Build a 2-layer LSTM + Dense(1) model and fit it."""
    cfg = get_scientific_config()
    val_split = cfg.lstm_validation_split if validation_split is None else validation_split

    model: Sequential = Sequential()
    model.add(
        LSTM(
            units=lstm_units,
            return_sequences=True,
            input_shape=(x_train.shape[1], x_train.shape[2]),
        )
    )
    model.add(LSTM(units=lstm_units))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mean_squared_error")
    model.fit(
        x_train,
        y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=val_split,
        verbose=0,
    )
    return model


def train_and_select_best_model(
    data: pd.DataFrame,
    property_name: str,
    model_path: Path | str,
    lstm_units_list: Sequence[int] | None = None,
    epochs_list: Sequence[int] | None = None,
    batch_size_list: Sequence[int] | None = None,
) -> None:
    """Grid-search LSTMs for milk and methane targets and persist artefacts."""
    cfg = get_scientific_config()
    units_grid = lstm_units_list or cfg.lstm_units_grid
    epochs_grid = epochs_list or cfg.lstm_epochs_grid
    batch_grid = batch_size_list or cfg.lstm_batch_size_grid

    property_data = data[data["Property"] == property_name].copy()
    property_data["Period"] = pd.to_datetime(property_data["Period"])
    property_data = property_data.set_index("Period")

    features = property_data[list(cfg.lstm_feature_columns)]
    target_milk = property_data[cfg.lstm_target_milk]
    target_methane = property_data[cfg.lstm_target_methane]

    scaler_features = MinMaxScaler(feature_range=(0, 1))
    scaler_target_milk = MinMaxScaler(feature_range=(0, 1))
    scaler_target_methane = MinMaxScaler(feature_range=(0, 1))

    scaled_features = scaler_features.fit_transform(features)
    scaled_target_milk = scaler_target_milk.fit_transform(target_milk.values.reshape(-1, 1))
    scaled_target_methane = scaler_target_methane.fit_transform(
        target_methane.values.reshape(-1, 1)
    )

    time_steps = cfg.lstm_time_steps
    x_milk, y_milk = create_sequences(scaled_features, scaled_target_milk, time_steps)
    x_methane, y_methane = create_sequences(scaled_features, scaled_target_methane, time_steps)

    split = int(cfg.lstm_train_fraction * len(x_milk))
    x_train_milk, x_test_milk = x_milk[:split], x_milk[split:]
    y_train_milk, y_test_milk = y_milk[:split], y_milk[split:]
    x_train_methane, x_test_methane = x_methane[:split], x_methane[split:]
    y_train_methane, y_test_methane = y_methane[:split], y_methane[split:]

    best_rmse_milk = float("inf")
    best_rmse_methane = float("inf")
    best_model_milk = None
    best_model_methane = None
    best_params_milk: tuple[int, int, int] | None = None
    best_params_methane: tuple[int, int, int] | None = None

    for lstm_units, epochs, batch_size in product(units_grid, epochs_grid, batch_grid):
        model_milk = build_and_train_lstm(
            x_train_milk, y_train_milk, lstm_units, epochs, batch_size
        )
        rmse_milk = float(
            np.sqrt(mean_squared_error(y_test_milk, model_milk.predict(x_test_milk, verbose=0)))
        )
        if rmse_milk < best_rmse_milk:
            best_rmse_milk = rmse_milk
            best_model_milk = model_milk
            best_params_milk = (lstm_units, epochs, batch_size)

        model_methane = build_and_train_lstm(
            x_train_methane, y_train_methane, lstm_units, epochs, batch_size
        )
        rmse_methane = float(
            np.sqrt(
                mean_squared_error(
                    y_test_methane, model_methane.predict(x_test_methane, verbose=0)
                )
            )
        )
        if rmse_methane < best_rmse_methane:
            best_rmse_methane = rmse_methane
            best_model_methane = model_methane
            best_params_methane = (lstm_units, epochs, batch_size)

    if best_model_milk is None or best_model_methane is None:
        raise RuntimeError(f"Training failed for property {property_name}")

    property_model_path = Path(model_path) / property_name
    property_model_path.mkdir(parents=True, exist_ok=True)

    best_model_milk.save(property_model_path / f"best_model_milk_{property_name}.keras")
    best_model_methane.save(property_model_path / f"best_model_methane_{property_name}.keras")
    np.save(property_model_path / f"scaler_features_{property_name}.npy", scaler_features)
    np.save(property_model_path / f"scaler_target_milk_{property_name}.npy", scaler_target_milk)
    np.save(
        property_model_path / f"scaler_target_methane_{property_name}.npy",
        scaler_target_methane,
    )
    np.save(property_model_path / f"best_params_milk_{property_name}.npy", best_params_milk)
    np.save(property_model_path / f"best_params_methane_{property_name}.npy", best_params_methane)

    logger.info(
        "Best model for %s saved (RMSE milk=%.6f, methane=%.6f)",
        property_name,
        best_rmse_milk,
        best_rmse_methane,
    )
