"""Scientific regression tests for Tier-1 emission baselines."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from enteric_emissions.config import get_paths, get_scientific_config
from enteric_emissions.domain.emissions import enrich_with_tier1_emissions

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "tier1_baselines.json"


@pytest.fixture(scope="module")
def baselines() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_scientific_config_matches_baseline_params(baselines: dict) -> None:
    cfg = get_scientific_config()
    expected = baselines["scientific_params"]
    assert cfg.emission_factor_dairy_cattle == expected["emission_factor_dairy_cattle"]
    assert cfg.emission_factor_other_cattle == expected["emission_factor_other_cattle"]
    assert cfg.gwp_ch4 == expected["gwp_ch4"]
    assert cfg.days_in_period == expected["days_in_period"]


def test_enriched_rows_match_reference_baselines(baselines: dict) -> None:
    paths = get_paths()
    df = pd.read_csv(paths.standardized_data, sep=";")
    enriched = enrich_with_tier1_emissions(df)

    for row in baselines["rows"]:
        match = enriched[
            (enriched["Property"] == row["Property"])
            & (enriched["Period"] == row["Period"])
        ]
        assert len(match) == 1
        got = match.iloc[0]
        assert got["Number_of_Dry_Cows"] == pytest.approx(row["N_other"])
        assert got["ef_enteric_kgCH4"] == pytest.approx(row["ef_enteric_kgCH4"])
        assert got["enteric_tCO2e"] == pytest.approx(row["enteric_tCO2e"])
