"""Unit tests for LSTM sequence construction."""

import numpy as np

from enteric_emissions.ml.sequences import create_sequences


def test_create_sequences_shapes():
    features = np.arange(20, dtype=float).reshape(10, 2)
    target = np.arange(10, dtype=float).reshape(10, 1)
    x, y = create_sequences(features, target, time_steps=3)
    assert x.shape == (7, 3, 2)
    assert y.shape == (7, 1)
    np.testing.assert_array_equal(x[0], features[0:3])
    np.testing.assert_array_equal(y[0], target[3])
