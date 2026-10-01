"""Enrich standardized data with Tier-1 enteric emission columns."""

from __future__ import annotations

import logging
from pathlib import Path

from enteric_emissions.config import get_paths
from enteric_emissions.data.io import load_csv, save_csv
from enteric_emissions.domain.emissions import enrich_with_tier1_emissions

logger = logging.getLogger(__name__)


def enrich_emissions_dataset(
    input_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    """Read standardized CSV, compute Tier-1 emissions, write enriched CSV."""
    paths = get_paths()
    src = input_path or paths.standardized_data
    dst = output_path or paths.enriched_data
    logger.info("Enriching emissions from %s", src)
    standardized = load_csv(src)
    enriched = enrich_with_tier1_emissions(standardized)
    save_csv(enriched, dst)
    logger.info("Wrote enriched dataset (%s rows) to %s", len(enriched), dst)
    return dst
