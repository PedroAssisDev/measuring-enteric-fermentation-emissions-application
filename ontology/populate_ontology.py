"""Compatibility shim — prefer scripts/ or enteric_emissions.ontology."""
from enteric_emissions.ontology.populate import populate_ontology_from_csv

if __name__ == "__main__":
    populate_ontology_from_csv()
