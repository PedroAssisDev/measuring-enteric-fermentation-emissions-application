"""Compatibility shim — prefer scripts/ or enteric_emissions.ontology."""
from enteric_emissions.ontology.create import generate_ontology

if __name__ == "__main__":
    generate_ontology(True)
