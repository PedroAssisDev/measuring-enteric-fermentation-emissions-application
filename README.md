# Measuring Enteric Fermentation Emissions Application

Software artefact associated with the CarbonSECO livestock services for quantifying, monitoring, and forecasting enteric fermentation emissions in Brazilian dairy farms.

## Objective

Provide reproducible services to:

1. Standardize dairy-property monitoring data.
2. Quantify baseline enteric CH₄ / tCO₂e using IPCC Tier 1 formulas as implemented in the case study.
3. Represent domain knowledge with **EntericMeasureOnto** (OWL + SWRL + Pellet).
4. Train/load per-property LSTM models for milk production and enteric emissions.
5. Support decision-making through an interactive Dash dashboard.

## Associated publication

This repository is the data and code artefact of:

**Silva, P. H. A., Braga, R., David, J. M., Neto, V. V. G., Arbex, W., & Stroele, V. (2026).**  
*Enhancing Carbon Emission Decisions in Livestock with CarbonSECO’s Service Suite.*  
In S. Hammoudi, A. Brodsky, J. Filipe, & M. Śmiałek (Eds.), *Enterprise Information Systems* (ICEIS 2024).  
Lecture Notes in Business Information Processing, vol. 566, pp. 323–341. Springer, Cham.

- **DOI:** [10.1007/978-3-032-08570-2_17](https://doi.org/10.1007/978-3-032-08570-2_17)
- **Springer chapter:** [https://link.springer.com/chapter/10.1007/978-3-032-08570-2_17](https://link.springer.com/chapter/10.1007/978-3-032-08570-2_17)
- **Print ISBN:** 978-3-032-08569-6 · **Online ISBN:** 978-3-032-08570-2
- **Series:** LNBIP (Lecture Notes in Business Information Processing)

### Abstract

Global concerns about the impact of agriculture, particularly regarding methane emissions from enteric fermentation in livestock, highlight the need for more effective strategies to mitigate these emissions. The CarbonSECO platform, designed to generate carbon credits in Brazilian rural areas, emerged in response to the growing importance of carbon credits to offset greenhouse gas (GHG) emissions. However, additional solutions are required to comprehensively address GHG emissions in the agricultural sector. This article extends the CarbonSECO platform, aiming to quantify, monitor, and control carbon emissions from enteric fermentation in livestock. Through ontologies and machine learning techniques, the platform provides solutions to assess and manage the environmental impact of livestock farming. These advancements directly address mitigating carbon emissions in Brazilian dairy farming. A case study involving 25 monitored farms demonstrates the platform’s ability to predict future emissions and milk production, offering decision-making tools for sustainable agricultural management. The results underscore the effectiveness of these services in promoting environmentally sustainable practices in livestock farming.

### Authors

| Author | Affiliation |
|--------|-------------|
| Pedro Henrique Assis Silva | Federal University of Juiz de Fora (UFJF), Brazil |
| Regina Braga | UFJF, Brazil |
| José Maria David | UFJF, Brazil |
| Valdemar Vicente Graciano Neto | Federal University of Goiás (UFG), Brazil |
| Wagner Arbex | UFJF / Embrapa Dairy Cattle, Brazil |
| Victor Stroele | UFJF, Brazil |

### Funding

Partially funded by UFJF/Brazil, CAPES/Brazil, CNPq/Brazil (grant 307194/2022-1), and FAPEMIG/Brazil (grants APQ-02685-17, APQ-02194-18).

## Architecture

```text
raw TSV
  → standardize (validate + period mapping)
  → enrich (Tier-1 enteric emissions)
  → ontology population (optional reasoner)
  → LSTM train/load (per property)
  → plots / dashboard / case-study metrics
```

Installable package: `src/enteric_emissions/`

| Module | Responsibility |
|--------|----------------|
| `config/` | Scientific + operational configuration |
| `domain/` | Tier-1 formulas (eqs. 1–2 behaviour) |
| `data/` | Schema, validation, standardization |
| `ontology/` | EntericMeasureOnto create/populate |
| `ml/` | Sequences, LSTM train/select, inference |
| `visualization/` | Offline forecast plots |
| `dashboard/` | Dash decision-support UI |
| `pipelines/` | Orchestration and CLI entrypoints |

## Requirements

- Python 3.10+
- Java runtime (only if running the Pellet reasoner via Owlready2)
- Optional GPU for TensorFlow training (pretrained models are provided)

## Installation

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -e ".[dev]"
```

Alternatively:

```bash
pip install -r requirements.txt
pip install -e .
```

## Configuration

- Scientific parameters: [`configs/scientific.yaml`](configs/scientific.yaml)  
  (EF dairy=87, EF other=56, GWP=28, days=30, LSTM window=3, grids, …)
- Operational paths/logging: [`configs/operational.yaml`](configs/operational.yaml)
- Optional env overrides: [`.env.example`](.env.example)

No API keys or credentials are required for the published case study.

## Data layout

| Path | Description |
|------|-------------|
| `data/raw/Property_data_orig.tsv` | Canonical raw dataset (25 farms, 386 monthly rows) |
| `data/raw/Property_data_orissg.tsv` | Unused alternate export (kept for traceability; do not use) |
| `data/processed/property_data_standardized.csv` | Standardized columns + calendar periods |
| `data/processed/property_data_enriched.csv` | + `Number_of_Dry_Cows`, `ef_enteric_kgCH4`, `enteric_tCO2e` |

## Execution

### 1) Standardize raw data

```bash
python scripts/standardize_dataset.py
```

### 2) Enrich with Tier-1 emissions

```bash
python scripts/enrich_emissions.py
```

### 3) Ontology (optional)

```bash
python scripts/build_ontology.py
python scripts/populate_ontology.py
```

### 4) LSTM plots (pretrained models; no retraining)

```bash
python scripts/generate_forecast_plots.py
# or
python scripts/train_lstm_models.py --plot
```

Pretrained artefacts exist for **P-1, P-2, P-3, P-12, P-22** under `models/`.

### 5) Train models (optional, expensive)

```bash
python scripts/train_lstm_models.py --train --properties P-1 P-12 --seed 42
```

### 6) Dashboard

```bash
python scripts/run_dashboard.py
# open http://127.0.0.1:8050
```

## Reproducing the case-study results

```bash
python experiments/reproduce_case_study.py
```

This writes KPI summaries to `results/metrics/case_study_kpis.json` and forecast plots for P-1 / P-12 to `results/plots/`.

## Running tests

```bash
pytest
```

Includes unit tests (formulas, period mapping, sequences), integration (standardize→enrich), and scientific regression baselines.

## Main technologies

Python, pandas, pydantic, scikit-learn, TensorFlow/Keras, Owlready2, Dash, Plotly, PyYAML, pytest, Ruff.

## Directory structure

```text
configs/                 scientific + operational YAML
data/raw|processed/      datasets
docs/                    project reports
experiments/             case-study reproduction scripts
legacy/                  pre-refactor prototypes (do not use)
models/                  pretrained Keras artefacts
ontology/owl_files/      EntericMeasureOnto OWL artefacts
results/                 plots and metrics
scripts/                 user-facing CLI wrappers
src/enteric_emissions/   installable library
tests/                   unit / integration / regression
```

## Citation

If you use this software, please cite:

```bibtex
@InProceedings{10.1007/978-3-032-08570-2_17,
  author    = {Silva, Pedro Henrique Assis
               and Braga, Regina
               and David, Jos{\'e} Maria
               and Neto, Valdemar Vicente Graciano
               and Arbex, Wagner
               and Stroele, Victor},
  editor    = {Hammoudi, Slimane
               and Brodsky, Alexander
               and Filipe, Joaquim
               and {\'{S}}mia{\l}ek, Micha{\l}},
  title     = {Enhancing Carbon Emission Decisions in Livestock with CarbonSECO's Service Suite},
  booktitle = {Enterprise Information Systems},
  year      = {2026},
  publisher = {Springer Nature Switzerland},
  address   = {Cham},
  pages     = {323--341},
  isbn      = {978-3-032-08570-2},
  doi       = {10.1007/978-3-032-08570-2_17}
}
```

Code and data: [https://github.com/PedroAssisDev/measuring-enteric-fermentation-emissions-application](https://github.com/PedroAssisDev/measuring-enteric-fermentation-emissions-application)

## License

No explicit license file was present in the original repository. Add a license before public redistribution if required by your institution.
