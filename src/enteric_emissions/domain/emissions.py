"""IPCC Tier-1 enteric fermentation formulas as implemented for the case study.

Scientific reference (associated paper eqs. 1–2):
    EFEnteric = EFProduction * N * Days
    BEEnteric = EFEnteric * GWP * 0.001   # tCO2e

Behaviour is intentionally preserved from the original research code.
"""

from __future__ import annotations

from typing import Sequence

import pandas as pd

from enteric_emissions.config import get_scientific_config

# Default columns used by the original implementation to form the
# "other cattle" group (stored historically as Number_of_Dry_Cows).
OTHER_CATTLE_COLUMNS: tuple[str, ...] = (
    "Dry_Cows",
    "Pregnant_Heifers",
    "Heifers_in_Raising",
    "Suckling_Calves_female",
    "Suckling_Calves_male",
    "Male_Calves_in_Raising",
    "Male_Calves_in_Fattening",
    "Draft_and_Breeding_Bulls",
    "Equines_and_Mules",
)


def calculate_enteric_emission_factor_kg_ch4(
    ef_production: float,
    animal_heads: float,
    days: float,
) -> float:
    """Compute EFEnteric (kg CH4) for one animal group.

    Parameters
    ----------
    ef_production:
        Average enteric CH4 emission factor for the group (IPCC Latin America
        table values 87 / 56 as used in the associated publication).
    animal_heads:
        Average number of heads in the group (N).
    days:
        Days spent on farm during the monitoring period (Days).
    """
    return float(ef_production) * float(animal_heads) * float(days)


def calculate_baseline_emissions_tco2e(ef_enteric_kg_ch4: float, gwp: float) -> float:
    """Convert enteric CH4 (kg) to baseline emissions in tCO2e (eq. 1)."""
    return (float(ef_enteric_kg_ch4) * float(gwp)) / 1000.0


def sum_other_cattle_heads(
    row: pd.Series,
    columns: Sequence[str] | None = None,
) -> float:
    """Sum heads counted as 'other cattle' in the original pipeline.

    Note: the aggregated value is stored as ``Number_of_Dry_Cows`` for
    historical compatibility with trained LSTM feature names.
    """
    cols = list(columns) if columns is not None else list(OTHER_CATTLE_COLUMNS)
    return float(row[cols].sum())


def enrich_with_tier1_emissions(data: pd.DataFrame) -> pd.DataFrame:
    """Add Tier-1 emission columns using the scientific configuration.

    Adds:
    - Number_of_Dry_Cows (legacy name for aggregated other-cattle heads)
    - ef_enteric_kgCH4
    - enteric_tCO2e
    """
    cfg = get_scientific_config()
    enriched = data.copy()
    enriched.columns = enriched.columns.str.strip()

    other_heads = enriched.apply(
        lambda row: sum_other_cattle_heads(row, cfg.other_cattle_columns),
        axis=1,
    )
    ef_dairy = enriched["Number_of_Lactating_Cows"].apply(
        lambda n: calculate_enteric_emission_factor_kg_ch4(
            cfg.emission_factor_dairy_cattle, n, cfg.days_in_period
        )
    )
    ef_other = other_heads.apply(
        lambda n: calculate_enteric_emission_factor_kg_ch4(
            cfg.emission_factor_other_cattle, n, cfg.days_in_period
        )
    )
    ef_total = ef_dairy + ef_other
    enriched["Number_of_Dry_Cows"] = other_heads
    enriched["ef_enteric_kgCH4"] = ef_total
    enriched["enteric_tCO2e"] = ef_total.apply(
        lambda ef: calculate_baseline_emissions_tco2e(ef, cfg.gwp_ch4)
    )
    return enriched
