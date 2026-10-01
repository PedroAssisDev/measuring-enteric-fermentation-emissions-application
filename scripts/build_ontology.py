#!/usr/bin/env python
"""CLI wrapper: build EntericMeasureOnto TBox."""

from enteric_emissions.config.settings import configure_logging
from enteric_emissions.ontology.create import generate_ontology

if __name__ == "__main__":
    configure_logging()
    generate_ontology(True)
