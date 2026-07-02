"""Small online models with no heavy ML dependency.

These models are deliberately simple. They provide a transparent baseline for a
research artifact; production systems can swap them for calibrated models from
scikit-learn, Vowpal Wabbit, River, or an internal online-learning stack.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from rt_cinfer_web.utils import sigmoid


@dataclass
class OnlineStandardizer:
    """Running mean/variance standardizer."""

    n_seen: int = 0
    mean_: np.ndarray | None = None
    m2_: np.ndarray | None = None
    eps: float = 1e-8

    def partial_fit(self, x: np.ndarray) -> "OnlineStandardizer":
        x = np.asarray(x, dtype=float)
        if x.ndim != 2:
            raise ValueError("x must be a 2D matrix")
        if self.mean_ is None:
            self.mean_ = np.zeros(x.shape[1], dtype=float)
            self.m2_ = np.zeros(x.shape[1], dtype=float)
        for row in x:
            self.n_seen += 1
            delta = row - self.mean_
            self.mean_ += delta / self.n_seen
            delta2 = row - self.mean_
            self.m2_ += delta * delta2
        return self

    @property
    def scale_(self) -> np.ndarray:
        if self.mean_ is None or self.m2_ is None or self.n_seen < 2:
            if self.mean_ is None:
                return np.array([1.0])
            return np.ones_like(self.mean_)
        var = self.m2_ / max(self.n_seen - 1, 1)
        return np.sqrt(np.maximum(var, self.eps))

    def transform(self, x: np.ndarray) -> np.ndarray:
        if self.mean_ is None:
            return np.asarray(x, dtype=float)
        return (np.asarray(x, dtype=float) - self.mean_) / self.scale_

    def fit_transform(self, x: np.ndarray) -> np.ndarray:
        self.partial_fit(x)
        return self.transform(x)


@dataclass
class OnlineLinearRegressor:
    """Mini-batch SGD linear regression."""

    n_features: int
    learning_rate: float = 0.02
    l2: float = 1e-4
    weights: np.ndarray = field(init=False)
    bias: float = 0.0
    fitted: bool = False

    def __post_init__(self) -> None:
        self.weights = np.zeros(self.n_features, dtype=float)

    def predict(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        return x @ self.weights + self.bias

    def partial_fit(self, x: np.ndarray, y: np.ndarray) -> "OnlineLinearRegressor":
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        if x.size == 0:
            return self
        pred = self.predict(x)
        err = pred - y
        grad_w = (x.T @ err) / len(y) + self.l2 * self.weights
        grad_b = float(np.mean(err))
        self.weights -= self.learning_rate * grad_w
        self.bias -= self.learning_rate * grad_b
        self.fitted = True
        return self


@dataclass
class OnlineLogisticRegressor:
    """Mini-batch SGD logistic regression."""

    n_features: int
    learning_rate: float = 0.02
    l2: float = 1e-4
    weights: np.ndarray = field(init=False)
    bias: float = 0.0
    fitted: bool = False

    def __post_init__(self) -> None:
        self.weights = np.zeros(self.n_features, dtype=float)

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        return sigmoid(x @ self.weights + self.bias)

    def partial_fit(self, x: np.ndarray, y: np.ndarray) -> "OnlineLogisticRegressor":
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        if x.size == 0:
            return self
        p = self.predict_proba(x)
        err = p - y
        grad_w = (x.T @ err) / len(y) + self.l2 * self.weights
        grad_b = float(np.mean(err))
        self.weights -= self.learning_rate * grad_w
        self.bias -= self.learning_rate * grad_b
        self.fitted = True
        return self
