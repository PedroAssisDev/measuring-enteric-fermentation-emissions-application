"""Console entrypoints registered in ``pyproject.toml``."""

from __future__ import annotations

import argparse
import logging

from enteric_emissions.config.settings import configure_logging, get_paths
from enteric_emissions.data.transform import standardize_dataset
from enteric_emissions.dashboard.app import run_dashboard
from enteric_emissions.ontology.create import generate_ontology
from enteric_emissions.ontology.populate import populate_ontology_from_csv
from enteric_emissions.pipelines.enrich import enrich_emissions_dataset
from enteric_emissions.pipelines.train import generate_plots_for_pretrained, train_properties

logger = logging.getLogger(__name__)


def standardize_main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(description="Standardize raw dairy TSV data")
    parser.add_argument(
        "--allow-invalid",
        action="store_true",
        help="Do not fail when invalid rows are found (not recommended).",
    )
    args = parser.parse_args()
    standardize_dataset(fail_on_invalid=not args.allow_invalid)


def enrich_main() -> None:
    configure_logging()
    enrich_emissions_dataset()


def train_main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(description="Train or plot LSTM models")
    parser.add_argument(
        "--train",
        action="store_true",
        help="Run training (default is to only plot using pretrained models).",
    )
    parser.add_argument(
        "--properties",
        nargs="*",
        default=None,
        help="Property ids to process (default: pretrained set or all).",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Generate one-step forecast plots for pretrained models.",
    )
    args = parser.parse_args()
    if args.train:
        train_properties(args.properties, seed=args.seed)
    if args.plot or not args.train:
        generate_plots_for_pretrained(args.properties)


def ontology_main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(description="Build/populate EntericMeasureOnto")
    parser.add_argument("--build-tbox", action="store_true")
    parser.add_argument("--populate", action="store_true")
    parser.add_argument("--no-reasoner", action="store_true")
    args = parser.parse_args()
    if args.build_tbox:
        generate_ontology(True)
    if args.populate or not args.build_tbox:
        populate_ontology_from_csv(run_reasoner=not args.no_reasoner)


def dashboard_main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(description="Run the CarbonSECO livestock dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8050)
    parser.add_argument("--no-debug", action="store_true")
    args = parser.parse_args()
    paths = get_paths()
    if not paths.enriched_data.exists():
        logger.info("Enriched data missing; generating it first")
        enrich_emissions_dataset()
    run_dashboard(host=args.host, port=args.port, debug=not args.no_debug)
