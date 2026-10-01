"""Machine-learning helpers for per-property LSTM models.

Heavy dependencies (Keras/TensorFlow) are imported by submodules on use so
lightweight utilities such as ``create_sequences`` remain testable without TF.
"""

from enteric_emissions.ml.sequences import create_sequences

__all__ = [
    "create_sequences",
    "build_and_train_lstm",
    "train_and_select_best_model",
    "load_property_artifacts",
    "predict_horizon",
    "predict_one_step",
]


def __getattr__(name: str):
    if name in {"build_and_train_lstm", "train_and_select_best_model"}:
        from enteric_emissions.ml import training

        return getattr(training, name)
    if name in {"load_property_artifacts", "predict_horizon", "predict_one_step"}:
        from enteric_emissions.ml import inference

        return getattr(inference, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
