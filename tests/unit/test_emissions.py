"""Unit tests for Tier-1 enteric emission formulas (current implementation)."""

from enteric_emissions.domain.emissions import (
    calculate_baseline_emissions_tco2e,
    calculate_enteric_emission_factor_kg_ch4,
)


def test_enteric_factor_matches_equation_2_behaviour():
    # EF = 87 * 23 * 30 = 60030
    assert calculate_enteric_emission_factor_kg_ch4(87, 23, 30) == 60030.0


def test_baseline_emissions_matches_equation_1_behaviour():
    # (117150 * 28) / 1000 = 3280.2
    assert calculate_baseline_emissions_tco2e(117150.0, 28.0) == 3280.2


def test_combined_dairy_and_other_for_p1_sample():
    dairy = calculate_enteric_emission_factor_kg_ch4(87, 23, 30)
    other = calculate_enteric_emission_factor_kg_ch4(56, 34, 30)
    total = dairy + other
    assert total == 117150.0
    assert calculate_baseline_emissions_tco2e(total, 28.0) == 3280.2
