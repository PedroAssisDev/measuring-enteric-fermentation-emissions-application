"""Unit tests for relative Period → calendar date mapping."""

from enteric_emissions.data.transform import adjust_period_to_date


def test_period_one_is_one_month_before_anchor():
    assert adjust_period_to_date(1, "2023-01-01") == "2022-12-01"


def test_period_twenty_five_maps_to_2020_12():
    assert adjust_period_to_date(25, "2023-01-01") == "2020-12-01"
