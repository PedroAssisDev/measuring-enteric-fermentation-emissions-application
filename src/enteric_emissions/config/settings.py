"""Configuration loading with portable paths relative to the repository root."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


def repo_root() -> Path:
    """Resolve the repository root (two levels above this package file, or env override)."""
    env_root = os.environ.get("ENTERIC_REPO_ROOT")
    if env_root:
        return Path(env_root).resolve()
    # src/enteric_emissions/config/settings.py -> repo root
    return Path(__file__).resolve().parents[3]


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Configuration file must contain a mapping: {path}")
    return data


@dataclass(frozen=True)
class ScientificConfig:
    emission_factor_dairy_cattle: float
    emission_factor_other_cattle: float
    gwp_ch4: float
    days_in_period: int
    other_cattle_columns: tuple[str, ...]
    period_anchor_date: str
    lstm_time_steps: int
    lstm_train_fraction: float
    lstm_validation_split: float
    lstm_feature_columns: tuple[str, ...]
    lstm_target_milk: str
    lstm_target_methane: str
    lstm_units_grid: tuple[int, ...]
    lstm_epochs_grid: tuple[int, ...]
    lstm_batch_size_grid: tuple[int, ...]
    forecast_horizon_months: int
    properties_with_pretrained_models: tuple[str, ...]


@dataclass(frozen=True)
class Paths:
    root: Path
    raw_data: Path
    unused_raw_data: Path
    standardized_data: Path
    enriched_data: Path
    models_dir: Path
    results_plots: Path
    results_metrics: Path
    ontology_dir: Path
    ontology_tbox: Path
    ontology_populated: Path
    ontology_reasoned: Path


@lru_cache(maxsize=1)
def get_scientific_config() -> ScientificConfig:
    cfg = _load_yaml(repo_root() / "configs" / "scientific.yaml")
    tier1 = cfg["tier1"]
    lstm = cfg["lstm"]
    grid = lstm["hyperparameter_grid"]
    return ScientificConfig(
        emission_factor_dairy_cattle=float(tier1["emission_factor_dairy_cattle"]),
        emission_factor_other_cattle=float(tier1["emission_factor_other_cattle"]),
        gwp_ch4=float(tier1["gwp_ch4"]),
        days_in_period=int(tier1["days_in_period"]),
        other_cattle_columns=tuple(cfg["other_cattle_columns"]),
        period_anchor_date=str(cfg["period_mapping"]["anchor_date"]),
        lstm_time_steps=int(lstm["time_steps"]),
        lstm_train_fraction=float(lstm["train_fraction"]),
        lstm_validation_split=float(lstm["validation_split"]),
        lstm_feature_columns=tuple(lstm["feature_columns"]),
        lstm_target_milk=str(lstm["target_milk"]),
        lstm_target_methane=str(lstm["target_methane"]),
        lstm_units_grid=tuple(int(x) for x in grid["lstm_units"]),
        lstm_epochs_grid=tuple(int(x) for x in grid["epochs"]),
        lstm_batch_size_grid=tuple(int(x) for x in grid["batch_size"]),
        forecast_horizon_months=int(lstm["forecast_horizon_months"]),
        properties_with_pretrained_models=tuple(cfg["properties_with_pretrained_models"]),
    )


@lru_cache(maxsize=1)
def get_paths() -> Paths:
    cfg = _load_yaml(repo_root() / "configs" / "operational.yaml")
    root = repo_root()
    path_cfg = cfg["paths"]

    def resolve(key: str) -> Path:
        return (root / path_cfg[key]).resolve()

    return Paths(
        root=root,
        raw_data=resolve("raw_data"),
        unused_raw_data=resolve("unused_raw_data"),
        standardized_data=resolve("standardized_data"),
        enriched_data=resolve("enriched_data"),
        models_dir=resolve("models_dir"),
        results_plots=resolve("results_plots"),
        results_metrics=resolve("results_metrics"),
        ontology_dir=resolve("ontology_dir"),
        ontology_tbox=resolve("ontology_tbox"),
        ontology_populated=resolve("ontology_populated"),
        ontology_reasoned=resolve("ontology_reasoned"),
    )


def configure_logging(level: str | None = None) -> None:
    """Configure root logging for CLI scripts."""
    resolved = level or os.environ.get("ENTERIC_LOG_LEVEL")
    if resolved is None:
        op = _load_yaml(repo_root() / "configs" / "operational.yaml")
        resolved = str(op.get("logging", {}).get("level", "INFO"))
    logging.basicConfig(
        level=getattr(logging, resolved.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
