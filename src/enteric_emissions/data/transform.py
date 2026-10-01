"""Raw TSV → standardized CSV transforms."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from enteric_emissions.config import get_paths, get_scientific_config
from enteric_emissions.data.io import load_csv, save_csv
from enteric_emissions.data.schema import STANDARDIZED_COLUMNS, validate_raw_dataframe

logger = logging.getLogger(__name__)


def adjust_period_to_date(period: int, anchor_date: str | None = None) -> str:
    """Map relative period integer N to calendar date (anchor - N months)."""
    cfg_anchor = anchor_date or get_scientific_config().period_anchor_date
    final_period = pd.Timestamp(cfg_anchor)
    return (final_period - pd.DateOffset(months=int(period))).strftime("%Y-%m-%d")


def standardize_raw_dataframe(
    df: pd.DataFrame,
    *,
    fail_on_invalid: bool = True,
) -> pd.DataFrame:
    """Validate, map Period to dates, and rename columns to standardized names."""
    validate_raw_dataframe(df, fail_on_invalid=fail_on_invalid)
    out = df.copy()
    out["Period"] = out["Period"].apply(adjust_period_to_date)
    out.columns = STANDARDIZED_COLUMNS
    return out


def standardize_dataset(
    input_path: Path | None = None,
    output_path: Path | None = None,
    *,
    fail_on_invalid: bool = True,
) -> Path:
    """Read raw TSV, standardize, and write processed CSV."""
    paths = get_paths()
    src = input_path or paths.raw_data
    dst = output_path or paths.standardized_data
    logger.info("Standardizing dataset from %s", src)
    raw = load_csv(src)
    standardized = standardize_raw_dataframe(raw, fail_on_invalid=fail_on_invalid)
    save_csv(standardized, dst)
    logger.info("Wrote standardized dataset (%s rows) to %s", len(standardized), dst)
    return dst
