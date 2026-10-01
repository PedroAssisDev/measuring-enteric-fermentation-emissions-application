"""Regression checks for persisted LSTM hyperparameter artefacts."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from enteric_emissions.config import get_paths

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "tier1_baselines.json"


def test_saved_best_params_match_baseline() -> None:
    expected = json.loads(FIXTURE.read_text(encoding="utf-8"))["model_params"]
    models_dir = get_paths().models_dir
    for property_name, params in expected.items():
        milk = np.load(
            models_dir / property_name / f"best_params_milk_{property_name}.npy",
            allow_pickle=True,
        )
        methane = np.load(
            models_dir / property_name / f"best_params_methane_{property_name}.npy",
            allow_pickle=True,
        )
        assert list(milk) == params["milk"]
        assert list(methane) == params["methane"]


@pytest.mark.parametrize("property_name", ["P-1", "P-2", "P-3", "P-12", "P-22"])
def test_keras_artifacts_exist(property_name: str) -> None:
    base = get_paths().models_dir / property_name
    assert (base / f"best_model_milk_{property_name}.keras").exists()
    assert (base / f"best_model_methane_{property_name}.keras").exists()
