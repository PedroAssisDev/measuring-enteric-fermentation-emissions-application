#!/usr/bin/env python
"""CLI wrapper: populate EntericMeasureOnto from standardized CSV."""

from enteric_emissions.config.settings import configure_logging
from enteric_emissions.ontology.populate import populate_ontology_from_csv

if __name__ == "__main__":
    configure_logging()
    populate_ontology_from_csv()
