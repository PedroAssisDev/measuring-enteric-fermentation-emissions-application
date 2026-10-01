# Refactoring Report

## 1. Executive summary

The repository was reorganized into an installable scientific software package (`enteric_emissions`) with explicit configuration, portable paths, CLI scripts, tests (including scientific regression baselines), a unified Dash dashboard, and documentation suitable for a publication artefact. Scientific formulas, parameters, and pretrained LSTM artefacts were preserved.

## 2. Previous architecture

Loosely coupled prototypes:

- `data/transform_data.py` — TSV standardization
- `ontology/` — OWL create/populate scripts
- `prediction project/` — Tier-1 enrichment + LSTM train/plot
- `model/` — Dash prototypes with absolute Linux paths
- `dashboard/` — incomplete stub

Duplicated CSVs and duplicated scientific constants; empty README; no tests.

## 3. New architecture

Single package under `src/enteric_emissions/` with:

- `config/` — YAML-driven scientific vs operational settings
- `domain/` — Tier-1 formulas
- `data/` — schema/validation/transform/IO
- `ontology/` — EntericMeasureOnto
- `ml/` — sequences, training, inference
- `visualization/` — offline plots
- `dashboard/` — unified UI (analytics + 3-month forecast modal)
- `pipelines/` — orchestration + console scripts

Data lives in `data/raw` and `data/processed`; models in `models/`; results in `results/`; old code in `legacy/`.

## 4. Main problems found

- Non-portable absolute paths
- Fragmented pipelines and duplicated datasets/constants
- Training entrypoint broken for properties without artefacts
- Missing tests and documentation
- Incomplete dashboard vs working prototypes

## 5. Changes by module

| Area | Change |
|------|--------|
| Packaging | Added `pyproject.toml`, installable package, entry points |
| Config | `configs/scientific.yaml`, `configs/operational.yaml` |
| Domain | Centralized Tier-1 math |
| Data | Validation (fail by default), portable transforms |
| Ontology | Path-safe create/populate; stable ontology IRI for new builds |
| ML | Extracted train/infer APIs; CLI `--train` / `--plot` |
| Dashboard | Unified KPIs + charts + forecast modal |
| Tests | Unit, integration, regression baselines |
| Docs | README + this report |
| Legacy | Moved prototypes to `legacy/` |

## 6. Removed / archived code

Moved to `legacy/` (not deleted): old `model/`, `prediction project/`, stub `dashboard/`, old data layout copies, original ontology scripts.  
`Property_data_orissg.tsv` retained under `data/raw/` and marked unused.

Unused FastAPI/uvicorn dependencies removed from the dependency set.

## 7. Dependencies

**Added / made explicit:** pydantic, PyYAML, matplotlib, dash-bootstrap-components, pytest, ruff.  
**Removed:** fastapi, uvicorn, statsmodels (unused in this artefact).  
**Kept:** pandas, numpy, scikit-learn, tensorflow, keras, owlready2, dash, plotly.

## 8. Tests

- Unit: emissions formulas, period mapping, sequence shapes
- Integration: standardize → enrich on full raw dataset
- Regression: Tier-1 baselines for P-1/P-12; saved LSTM hyperparameter artefacts for five properties

## 9. Reproducibility

```bash
pip install -e ".[dev]"
python scripts/standardize_dataset.py
python scripts/enrich_emissions.py
python scripts/generate_forecast_plots.py
python scripts/run_dashboard.py
pytest
```

Pretrained models are used by default; training is opt-in.

## 10. Scientific compatibility

Tier-1 emission baselines for reference rows are numerically identical before/after refactoring (see regression fixtures).  
LSTM weights were not re-trained; artefacts were copied to `models/`.

## 11. Future improvements

- Expand pretrained model coverage beyond five properties after a documented retraining protocol with seeds and metrics on physical scale.
- Continue improving forecast and ontology integration pathways as the CarbonSECO livestock services evolve.
