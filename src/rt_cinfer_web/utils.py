"""Small numerical utilities used across the package."""

from __future__ import annotations

import math
from collections.abc import Iterable

import numpy as np
import pandas as pd


def sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.clip(z, -40, 40)
    return 1.0 / (1.0 + np.exp(-z))


def z_value(confidence: float) -> float:
    """Return common normal quantiles without requiring scipy."""

    table = {
        0.80: 1.2816,
        0.85: 1.4395,
        0.90: 1.6449,
        0.95: 1.9600,
        0.975: 2.2414,
        0.99: 2.5758,
    }
    return table.get(round(confidence, 3), 1.96)


def as_2d_numeric(df: pd.DataFrame, columns: Iterable[str]) -> np.ndarray:
    """Convert selected columns to a dense numeric matrix."""

    cols = list(columns)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df[cols].astype(float).to_numpy(copy=True)


def safe_mean(x: Iterable[float], default: float = float("nan")) -> float:
    arr = np.asarray(list(x), dtype=float)
    if arr.size == 0:
        return default
    return float(np.nanmean(arr))


def rolling_chunks(df: pd.DataFrame, batch_size: int):
    for start in range(0, len(df), batch_size):
        yield df.iloc[start : start + batch_size].copy()


def finite_or(value: float, fallback: float = 0.0) -> float:
    return float(value) if math.isfinite(float(value)) else fallback
