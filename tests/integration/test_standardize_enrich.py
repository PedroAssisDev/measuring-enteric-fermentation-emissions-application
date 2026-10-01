"""Integration test for standardize → enrich pipeline on real raw data."""

from pathlib import Path

import pandas as pd

from enteric_emissions.data.transform import standardize_raw_dataframe
from enteric_emissions.domain.emissions import enrich_with_tier1_emissions
from enteric_emissions.config import get_paths


def test_standardize_and_enrich_row_count() -> None:
    paths = get_paths()
    raw = pd.read_csv(paths.raw_data, sep=";")
    standardized = standardize_raw_dataframe(raw, fail_on_invalid=True)
    enriched = enrich_with_tier1_emissions(standardized)
    assert len(enriched) == len(raw)
    assert {"ef_enteric_kgCH4", "enteric_tCO2e", "Number_of_Dry_Cows"}.issubset(
        enriched.columns
    )
    assert enriched["Property"].nunique() == 25
