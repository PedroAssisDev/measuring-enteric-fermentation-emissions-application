#!/usr/bin/env python
"""CLI wrapper: enrich standardized data with Tier-1 enteric emissions."""

from enteric_emissions.pipelines.cli import enrich_main

if __name__ == "__main__":
    enrich_main()
