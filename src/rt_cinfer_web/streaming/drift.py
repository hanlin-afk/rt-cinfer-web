"""Drift detectors for streaming Web Vitals."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class PageHinkleyDetector:
    """Simple Page-Hinkley detector for mean shifts."""

    delta: float = 0.005
    threshold: float = 40.0
    alpha: float = 0.999
    mean: float = 0.0
    cumulative: float = 0.0
    min_cumulative: float = 0.0
    n: int = 0
    drift_detected: bool = False

    def update(self, values) -> bool:
        for value in np.asarray(values, dtype=float):
            self.n += 1
            if self.n == 1:
                self.mean = float(value)
            else:
                self.mean = self.alpha * self.mean + (1 - self.alpha) * float(value)
            self.cumulative += float(value) - self.mean - self.delta
            self.min_cumulative = min(self.min_cumulative, self.cumulative)
            if self.cumulative - self.min_cumulative > self.threshold:
                self.drift_detected = True
        return self.drift_detected

    def reset(self) -> None:
        self.mean = 0.0
        self.cumulative = 0.0
        self.min_cumulative = 0.0
        self.n = 0
        self.drift_detected = False


@dataclass
class PopulationStabilityIndex:
    """PSI detector comparing a reference and recent feature distribution."""

    feature: str
    bins: int = 10
    min_reference: int = 500
    recent_size: int = 500
    threshold: float = 0.2
    reference: deque[float] = field(default_factory=deque)
    recent: deque[float] = field(default_factory=deque)

    def update(self, batch: pd.DataFrame) -> tuple[float, bool]:
        values = batch[self.feature].astype(float).to_numpy()
        for v in values:
            if len(self.reference) < self.min_reference:
                self.reference.append(float(v))
            else:
                self.recent.append(float(v))
                if len(self.recent) > self.recent_size:
                    self.recent.popleft()
        if len(self.reference) < self.min_reference or len(self.recent) < max(50, self.recent_size // 4):
            return 0.0, False
        psi = self._psi(np.asarray(self.reference), np.asarray(self.recent))
        return psi, bool(psi >= self.threshold)

    def _psi(self, reference: np.ndarray, recent: np.ndarray) -> float:
        quantiles = np.linspace(0, 1, self.bins + 1)
        edges = np.unique(np.quantile(reference, quantiles))
        if len(edges) < 3:
            return 0.0
        ref_counts, _ = np.histogram(reference, bins=edges)
        rec_counts, _ = np.histogram(recent, bins=edges)
        ref_prop = np.clip(ref_counts / max(ref_counts.sum(), 1), 1e-5, None)
        rec_prop = np.clip(rec_counts / max(rec_counts.sum(), 1), 1e-5, None)
        return float(np.sum((rec_prop - ref_prop) * np.log(rec_prop / ref_prop)))
