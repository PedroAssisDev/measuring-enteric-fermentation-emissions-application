# Legacy code archive

This directory stores the pre-refactoring research prototypes preserved for
traceability. Prefer the installable package under `src/enteric_emissions/` and
the scripts in `scripts/`.

| Path | Former role |
|------|-------------|
| `model/` | Absolute-path Dash prototypes (`bbbb.py`, `predict.py`, `predict2.py`) |
| `prediction_project/` | Original LSTM training/plotting package |
| `dashboard/` | Incomplete Dash scaffold |
| `transform_data.py` | Original TSV→CSV script |
| `data_orig/`, `data_standardized/` | Previous data layout (now `data/raw` and `data/processed`) |
| `create_ontology.py`, `populate_ontology.py` | Original ontology entrypoints |

Do not use these modules for new work.
