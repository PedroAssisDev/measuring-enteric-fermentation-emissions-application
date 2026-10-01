"""Sliding-window sequence construction for LSTM training."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt


def create_sequences(
    features: npt.NDArray[np.floating],
    target: npt.NDArray[np.floating],
    time_steps: int = 3,
) -> tuple[npt.NDArray[np.floating], npt.NDArray[np.floating]]:
    """Build supervised sequences where y is the target at t + time_steps."""
    x_list: list[npt.NDArray[np.floating]] = []
    y_list: list[npt.NDArray[np.floating]] = []
    for i in range(len(features) - time_steps):
        x_list.append(features[i : i + time_steps])
        y_list.append(target[i + time_steps])
    return np.array(x_list), np.array(y_list)
