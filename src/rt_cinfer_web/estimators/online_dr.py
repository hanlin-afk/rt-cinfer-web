"""Online doubly robust causal-effect estimation."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from rt_cinfer_web.config import EstimatorConfig
from rt_cinfer_web.estimators.models import OnlineStandardizer
from rt_cinfer_web.utils import as_2d_numeric, z_value


@dataclass(frozen=True)
class CausalEstimate:
    """A streaming causal estimate for a single treatment/outcome pair."""

    treatment: str
    outcome: str
    ate: float
    standard_error: float
    ci_low: float
    ci_high: float
    n: int
    treated_fraction: float
    overlap_rate: float
    identifiable: bool
    warning: str | None = None

    @property
    def is_latency_improving(self) -> bool:
        return self.ci_high < 0

    def as_dict(self) -> dict[str, float | int | bool | str | None]:
        return {
            "treatment": self.treatment,
            "outcome": self.outcome,
            "ate": self.ate,
            "standard_error": self.standard_error,
            "ci_low": self.ci_low,
            "ci_high": self.ci_high,
            "n": self.n,
            "treated_fraction": self.treated_fraction,
            "overlap_rate": self.overlap_rate,
            "identifiable": self.identifiable,
            "warning": self.warning,
        }


@dataclass
class OnlineDoublyRobustEstimator:
    """Streaming AIPW estimator for average treatment effects.

    The estimator keeps a bounded rolling history. At each update, it scores the
    new batch using nuisance models fit on prior history, then incorporates the
    batch into the history. This is an online, prequential design: the current
    batch is evaluated out-of-sample relative to the nuisance models.

    Nuisance models are intentionally transparent rolling ridge regressions. The
    propensity nuisance is a clipped linear-probability model; production users
    can replace it with a calibrated online classifier without changing the AIPW
    score.
    """

    features: tuple[str, ...]
    treatment: str
    outcome: str
    config: EstimatorConfig = field(default_factory=EstimatorConfig)
    identifiable_assumption: bool = True

    def __post_init__(self) -> None:
        self.standardizer = OnlineStandardizer()
        self._psi: deque[float] = deque(maxlen=self.config.max_history)
        self._treatment_history: deque[float] = deque(maxlen=self.config.max_history)
        self._overlap_history: deque[float] = deque(maxlen=self.config.max_history)
        self._x_history: deque[np.ndarray] = deque(maxlen=self.config.max_history)
        self._a_history: deque[float] = deque(maxlen=self.config.max_history)
        self._y_history: deque[float] = deque(maxlen=self.config.max_history)
        self._last_warning: str | None = None

    def update(self, batch: pd.DataFrame) -> CausalEstimate:
        x_raw = as_2d_numeric(batch, self.features)
        if self.config.stabilize_features:
            if self.standardizer.n_seen == 0:
                self.standardizer.partial_fit(x_raw)
            x = self.standardizer.transform(x_raw)
        else:
            x = x_raw

        a = batch[self.treatment].astype(float).to_numpy()
        y = batch[self.outcome].astype(float).to_numpy()

        e = self._predict_propensity(x, observed=a)
        m1, m0 = self._predict_outcomes(x, observed_y=y)
        e_clip = np.clip(e, self.config.propensity_clip, 1 - self.config.propensity_clip)
        psi = m1 - m0 + a * (y - m1) / e_clip - (1 - a) * (y - m0) / (1 - e_clip)

        overlap = ((e >= self.config.propensity_clip) & (e <= 1 - self.config.propensity_clip)).astype(float)
        self._psi.extend(psi.tolist())
        self._treatment_history.extend(a.tolist())
        self._overlap_history.extend(overlap.tolist())

        # Store current batch after scoring. This preserves online/prequential evaluation.
        self._x_history.extend([row.copy() for row in x])
        self._a_history.extend(a.tolist())
        self._y_history.extend(y.tolist())
        if self.config.stabilize_features:
            self.standardizer.partial_fit(x_raw)

        return self.estimate()

    def estimate(self) -> CausalEstimate:
        scores = np.asarray(self._psi, dtype=float)
        n = int(scores.size)
        if n == 0:
            return CausalEstimate(
                self.treatment,
                self.outcome,
                float("nan"),
                float("nan"),
                float("nan"),
                float("nan"),
                0,
                0.0,
                0.0,
                False,
                "No observations have been processed.",
            )
        ate = float(np.mean(scores))
        se = float(np.std(scores, ddof=1) / np.sqrt(n)) if n > 1 else float("inf")
        z = z_value(self.config.confidence)
        ci_low, ci_high = ate - z * se, ate + z * se
        treated_fraction = float(np.mean(np.asarray(self._treatment_history)))
        overlap_rate = float(np.mean(np.asarray(self._overlap_history)))
        warnings: list[str] = []
        if n < self.config.min_samples:
            warnings.append(f"Only {n} observations; minimum configured sample is {self.config.min_samples}.")
        if overlap_rate < 1 - self.config.min_overlap:
            warnings.append("Limited propensity overlap after clipping.")
        if treated_fraction < self.config.min_overlap or treated_fraction > 1 - self.config.min_overlap:
            warnings.append("Treatment share is near 0 or 1; effect may be weakly identified.")
        identifiable = self.identifiable_assumption and not any("weakly identified" in w for w in warnings)
        self._last_warning = " ".join(warnings) if warnings else None
        return CausalEstimate(
            treatment=self.treatment,
            outcome=self.outcome,
            ate=ate,
            standard_error=se,
            ci_low=float(ci_low),
            ci_high=float(ci_high),
            n=n,
            treated_fraction=treated_fraction,
            overlap_rate=overlap_rate,
            identifiable=identifiable,
            warning=self._last_warning,
        )

    def _predict_propensity(self, x: np.ndarray, observed: np.ndarray) -> np.ndarray:
        if len(self._a_history) < max(50, len(self.features) * 5):
            p = (float(np.sum(observed)) + 1.0) / (len(observed) + 2.0)
            return np.repeat(p, len(observed))
        x_hist, a_hist, _ = self._history_arrays()
        beta = self._ridge_fit(x_hist, a_hist, l2=max(self.config.l2, 1e-3))
        p = self._add_intercept(x) @ beta
        return np.clip(p, 0.001, 0.999)

    def _predict_outcomes(self, x: np.ndarray, observed_y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        if len(self._y_history) < max(50, len(self.features) * 5):
            global_mean = float(np.mean(observed_y))
            return np.repeat(global_mean, len(observed_y)), np.repeat(global_mean, len(observed_y))
        x_hist, a_hist, y_hist = self._history_arrays()
        global_mean = float(np.mean(y_hist))
        if np.sum(a_hist == 1) >= len(self.features) + 2:
            beta1 = self._ridge_fit(x_hist[a_hist == 1], y_hist[a_hist == 1], l2=self.config.l2)
            m1 = self._add_intercept(x) @ beta1
        else:
            m1 = np.repeat(global_mean, len(x))
        if np.sum(a_hist == 0) >= len(self.features) + 2:
            beta0 = self._ridge_fit(x_hist[a_hist == 0], y_hist[a_hist == 0], l2=self.config.l2)
            m0 = self._add_intercept(x) @ beta0
        else:
            m0 = np.repeat(global_mean, len(x))
        return m1, m0

    def _history_arrays(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        return (
            np.asarray(self._x_history, dtype=float),
            np.asarray(self._a_history, dtype=float),
            np.asarray(self._y_history, dtype=float),
        )

    @staticmethod
    def _add_intercept(x: np.ndarray) -> np.ndarray:
        return np.column_stack([np.ones(len(x)), np.asarray(x, dtype=float)])

    def _ridge_fit(self, x: np.ndarray, y: np.ndarray, l2: float) -> np.ndarray:
        design = self._add_intercept(x)
        penalty = np.eye(design.shape[1]) * l2
        penalty[0, 0] = 0.0
        lhs = design.T @ design + penalty
        rhs = design.T @ np.asarray(y, dtype=float)
        try:
            return np.linalg.solve(lhs, rhs)
        except np.linalg.LinAlgError:
            return np.linalg.pinv(lhs) @ rhs

    def reset(self) -> None:
        self.__post_init__()
