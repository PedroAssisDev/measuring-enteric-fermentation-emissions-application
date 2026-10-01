#!/usr/bin/env python
"""Reproduce key case-study artefacts for properties P-1 and P-12.

Writes KPI summaries and one-step forecast plots under ``results/``.
"""

from __future__ import annotations

import json
import logging

from enteric_emissions.config.settings import configure_logging, get_paths
from enteric_emissions.dashboard.indicators import compute_kpi_values
from enteric_emissions.data.io import load_csv
from enteric_emissions.pipelines.enrich import enrich_emissions_dataset
from enteric_emissions.pipelines.train import generate_plots_for_pretrained

logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging()
    paths = get_paths()
    if not paths.enriched_data.exists():
        enrich_emissions_dataset()

    df = load_csv(paths.enriched_data)
    summary = {}
    for prop in ("P-1", "P-12"):
        subset = df[df["Property"] == prop]
        summary[prop] = compute_kpi_values(subset)
        logger.info("KPIs for %s: %s", prop, summary[prop])

    paths.results_metrics.mkdir(parents=True, exist_ok=True)
    out = paths.results_metrics / "case_study_kpis.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    logger.info("Wrote %s", out)

    generate_plots_for_pretrained(["P-1", "P-12"])


if __name__ == "__main__":
    main()
