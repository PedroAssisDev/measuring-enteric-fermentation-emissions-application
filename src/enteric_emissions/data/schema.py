"""Pydantic schema for raw dairy property records."""

from __future__ import annotations

import logging

import pandas as pd
from pydantic import BaseModel, ValidationError, field_validator

logger = logging.getLogger(__name__)

RAW_COLUMN_MAP: dict[str, str] = {
    "Property": "Property",
    "Period": "Period",
    "Milk Production (liters/month)": "Milk_Production",
    "Milk Sales (liters/month)": "Milk_Sales",
    "Milk Gross Price (R$/liter)": "Milk_Gross_Price",
    "Number of Lactating Cows": "Number_of_Lactating_Cows",
    "Employees During the Month (man-days/month)": "Employees_During_the_Month",
    "Area Used for Dairy Activity (ha)": "Area_Used_for_Dairy_Activity",
    "Reproducers": "Reproducers",
    "Lactating Cows": "Lactating_Cows",
    "Dry Cows": "Dry_Cows",
    "Pregnant Heifers": "Pregnant_Heifers",
    "Heifers in Raising": "Heifers_in_Raising",
    "Suckling Calves (female)": "Suckling_Calves_female",
    "Suckling Calves (male)": "Suckling_Calves_male",
    "Male Calves in Raising": "Male_Calves_in_Raising",
    "Male Calves in Fattening": "Male_Calves_in_Fattening",
    "Draft and Breeding Bulls": "Draft_and_Breeding_Bulls",
    "Equines and Mules": "Equines_and_Mules",
}

STANDARDIZED_COLUMNS: list[str] = [
    "Property",
    "Period",
    "Milk_Production",
    "Milk_Sales",
    "Milk_Gross_Price",
    "Number_of_Lactating_Cows",
    "Employees_During_the_Month",
    "Area_Used_for_Dairy_Activity",
    "Reproducers",
    "Lactating_Cows",
    "Dry_Cows",
    "Pregnant_Heifers",
    "Heifers_in_Raising",
    "Suckling_Calves_female",
    "Suckling_Calves_male",
    "Male_Calves_in_Raising",
    "Male_Calves_in_Fattening",
    "Draft_and_Breeding_Bulls",
    "Equines_and_Mules",
]


class DairyData(BaseModel):
    """Validated dairy monthly observation (raw-field semantics after mapping)."""

    Property: str
    Period: int
    Milk_Production: float
    Milk_Sales: float
    Milk_Gross_Price: float
    Number_of_Lactating_Cows: float
    Employees_During_the_Month: float
    Area_Used_for_Dairy_Activity: float
    Reproducers: float
    Lactating_Cows: float
    Dry_Cows: float
    Pregnant_Heifers: float
    Heifers_in_Raising: float
    Suckling_Calves_female: float
    Suckling_Calves_male: float
    Male_Calves_in_Raising: float
    Male_Calves_in_Fattening: float
    Draft_and_Breeding_Bulls: float
    Equines_and_Mules: float

    @field_validator("Period")
    @classmethod
    def period_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Period must be a positive integer")
        return value

    @field_validator(
        "Milk_Production",
        "Milk_Sales",
        "Milk_Gross_Price",
        "Area_Used_for_Dairy_Activity",
    )
    @classmethod
    def value_must_be_non_negative(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Value must be non-negative")
        return value

    @field_validator(
        "Number_of_Lactating_Cows",
        "Employees_During_the_Month",
        "Reproducers",
        "Lactating_Cows",
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
    @classmethod
    def count_must_be_non_negative(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Count must be non-negative")
        return value


def validate_raw_row(row: pd.Series) -> bool:
    """Validate one raw TSV row against ``DairyData``."""
    try:
        DairyData(
            Property=row["Property"],
            Period=row["Period"],
            Milk_Production=row["Milk Production (liters/month)"],
            Milk_Sales=row["Milk Sales (liters/month)"],
            Milk_Gross_Price=row["Milk Gross Price (R$/liter)"],
            Number_of_Lactating_Cows=row["Number of Lactating Cows"],
            Employees_During_the_Month=row["Employees During the Month (man-days/month)"],
            Area_Used_for_Dairy_Activity=row["Area Used for Dairy Activity (ha)"],
            Reproducers=row["Reproducers"],
            Lactating_Cows=row["Lactating Cows"],
            Dry_Cows=row["Dry Cows"],
            Pregnant_Heifers=row["Pregnant Heifers"],
            Heifers_in_Raising=row["Heifers in Raising"],
            Suckling_Calves_female=row["Suckling Calves (female)"],
            Suckling_Calves_male=row["Suckling Calves (male)"],
            Male_Calves_in_Raising=row["Male Calves in Raising"],
            Male_Calves_in_Fattening=row["Male Calves in Fattening"],
            Draft_and_Breeding_Bulls=row["Draft and Breeding Bulls"],
            Equines_and_Mules=row["Equines and Mules"],
        )
        return True
    except (ValidationError, KeyError) as exc:
        logger.error("Invalid row %s: %s", getattr(row, "name", "?"), exc)
        return False


def validate_raw_dataframe(df: pd.DataFrame, *, fail_on_invalid: bool = True) -> pd.Series:
    """Validate all rows. Raise if any invalid when ``fail_on_invalid`` is True."""
    valid_mask = df.apply(validate_raw_row, axis=1)
    invalid_count = int((~valid_mask).sum())
    if invalid_count and fail_on_invalid:
        raise ValueError(
            f"Found {invalid_count} invalid row(s) in raw dataset. "
            "Fix the source data or re-run with fail_on_invalid=False."
        )
    if invalid_count:
        logger.warning("Proceeding with %s invalid row(s) marked in the mask", invalid_count)
    return valid_mask
