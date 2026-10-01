"""Populate EntericMeasureOnto ABox from the standardized property CSV."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from owlready2 import get_ontology, sync_reasoner_pellet

from enteric_emissions.config import get_paths, get_scientific_config
from enteric_emissions.ontology.create import generate_ontology

logger = logging.getLogger(__name__)


def populate_ontology_from_csv(
    csv_path: Path | str | None = None,
    *,
    run_reasoner: bool = True,
) -> None:
    """Populate the ontology with data from a standardized CSV file."""
    paths = get_paths()
    cfg = get_scientific_config()
    source = Path(csv_path) if csv_path is not None else paths.standardized_data

    if paths.ontology_tbox.is_file():
        onto = get_ontology(str(paths.ontology_tbox)).load()
    else:
        generate_ontology(True)
        onto = get_ontology(str(paths.ontology_tbox)).load()

    data = pd.read_csv(source, sep=";")
    gwp = cfg.gwp_ch4
    ef_dairy = cfg.emission_factor_dairy_cattle
    ef_other = cfg.emission_factor_other_cattle

    with onto:
        for _, record in data.iterrows():
            property_name = record["Property"]
            matches = onto.search(iri=f"*{property_name}_Property")
            if not matches:
                prop = onto.RuralProperty(f"{property_name}_Property")
                prop.propertyName.append(property_name)
                prop.gwp.append(gwp)

                baseline_tier1 = onto.BaseLineEmissionsTier1(
                    f"{property_name}_BaseLineEmissionsTier1"
                )
                baseline_tier1.emissionFactorDairyCattleTier1.append(ef_dairy)
                baseline_tier1.emissionFactorOtherCattleTier1.append(ef_other)
                prop.HasBaseLineEmissions.append(baseline_tier1)
            else:
                prop = matches[0]

            monthly_production = onto.MonthlyProduction(
                f"{property_name}_MonthlyProduction_{record['Period']}"
            )
            monthly_production.measurementDate.append(
                datetime.strptime(record["Period"], "%Y-%m-%d")
            )
            monthly_production.milkProduction.append(float(record["Milk_Production"]))
            monthly_production.milkSales.append(float(record["Milk_Sales"]))
            prop.HasMonthlyProduction.append(monthly_production)

            prop.milkGrossPrice.append(float(record["Milk_Gross_Price"]))
            prop.monthlyDairyCattleTotal.append(int(record["Number_of_Lactating_Cows"]))
            prop.employeesDuringTheMonth.append(int(record["Employees_During_the_Month"]))
            prop.propertySizeForDairyActivity.append(
                float(record["Area_Used_for_Dairy_Activity"])
            )
            prop.monthlyOtherCattleTotal.append(
                float(record[list(cfg.other_cattle_columns)].sum())
            )

    onto.save(str(paths.ontology_populated))
    logger.info("Saved populated ontology to %s", paths.ontology_populated)

    if run_reasoner:
        try:
            sync_reasoner_pellet(
                infer_property_values=True, infer_data_property_values=True
            )
            onto.save(file=str(paths.ontology_reasoned), format="rdfxml")
            logger.info("Saved reasoned ontology to %s", paths.ontology_reasoned)
        except Exception as exc:  # Pellet/Java failures are environment-dependent
            logger.error("Reasoner inference failed: %s", exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    populate_ontology_from_csv()
