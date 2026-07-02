"""Bootstrap helpers for estimator diagnostics."""

from __future__ import annotations

import numpy as np


def bootstrap_mean_ci(values, confidence: float = 0.95, n_bootstrap: int = 500, seed: int = 3) -> tuple[float, float]:
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        means[i] = np.mean(rng.choice(arr, size=arr.size, replace=True))
    alpha = 1 - confidence
    return float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2))
