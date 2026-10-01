"""CSV I/O helpers using the project semicolon convention."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_csv(path: Path | str, *, sep: str = ";") -> pd.DataFrame:
    """Load a project CSV/TSV-like file."""
    return pd.read_csv(path, sep=sep)


def save_csv(df: pd.DataFrame, path: Path | str, *, sep: str = ";", index: bool = False) -> None:
    """Persist a DataFrame with project defaults."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep=sep, index=index)
