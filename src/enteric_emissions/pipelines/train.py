"""Train or load LSTM models for selected properties."""

from __future__ import annotations

import logging
import os
import random
from pathlib import Path

import numpy as np
import pandas as pd

from enteric_emissions.config import get_paths, get_scientific_config
from enteric_emissions.data.io import load_csv
from enteric_emissions.domain.emissions import enrich_with_tier1_emissions
from enteric_emissions.ml.inference import load_property_artifacts
from enteric_emissions.ml.training import train_and_select_best_model
from enteric_emissions.visualization.forecast_plots import plot_property_data

logger = logging.getLogger(__name__)


def _set_seeds(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import tensorflow as tf

        tf.random.set_seed(seed)
    except Exception as exc:  # pragma: no cover - TF optional at import time
        logger.warning("Could not set TensorFlow seed: %s", exc)


def load_enriched_training_frame(data_path: Path | None = None) -> pd.DataFrame:
    paths = get_paths()
    path = data_path or paths.enriched_data
    if path.exists():
        df = load_csv(path)
    else:
        df = enrich_with_tier1_emissions(load_csv(paths.standardized_data))
    df["Period"] = pd.to_datetime(df["Period"])
    return df


def train_properties(
    properties: list[str] | None = None,
    *,
    drop_last_period: bool = True,
    seed: int = 42,
) -> None:
    """Train LSTM models for the requested properties."""
    cfg = get_scientific_config()
    paths = get_paths()
    _set_seeds(seed)
    df = load_enriched_training_frame()
    if drop_last_period:
        last_idx = df.groupby("Property")["Period"].idxmax()
        df = df.drop(last_idx)

    targets = properties or list(df["Property"].unique())
    for property_name in targets:
        logger.info("Training models for %s", property_name)
        train_and_select_best_model(df, property_name, paths.models_dir)


def generate_plots_for_pretrained(
    properties: list[str] | None = None,
) -> None:
    """Generate one-step forecast plots for properties with saved artefacts."""
    cfg = get_scientific_config()
    paths = get_paths()
    df = load_enriched_training_frame()
    props = properties or list(cfg.properties_with_pretrained_models)
    for property_name in props:
        artifacts = load_property_artifacts(paths.models_dir, property_name)
        plot_property_data(df, property_name, paths.results_plots, artifacts)
