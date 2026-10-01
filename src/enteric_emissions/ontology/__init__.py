"""EntericMeasureOnto creation and population helpers."""

from enteric_emissions.ontology.create import generate_ontology
from enteric_emissions.ontology.populate import populate_ontology_from_csv

__all__ = ["generate_ontology", "populate_ontology_from_csv"]
