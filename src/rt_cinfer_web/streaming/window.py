"""Rolling window helpers."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np


@dataclass
class RollingWindow:
    maxlen: int = 5000
    values: deque[float] = field(init=False)

    def __post_init__(self) -> None:
        self.values = deque(maxlen=self.maxlen)

    def extend(self, items) -> None:
        self.values.extend([float(v) for v in items])

    def mean(self) -> float:
        arr = np.asarray(self.values, dtype=float)
        return float(np.mean(arr)) if arr.size else float("nan")

    def std(self) -> float:
        arr = np.asarray(self.values, dtype=float)
        return float(np.std(arr, ddof=1)) if arr.size > 1 else float("nan")

    def quantile(self, q: float) -> float:
        arr = np.asarray(self.values, dtype=float)
        return float(np.quantile(arr, q)) if arr.size else float("nan")
