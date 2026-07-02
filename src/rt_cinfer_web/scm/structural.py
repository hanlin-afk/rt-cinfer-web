"""Structural equations for counterfactual web-vitals simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

StructuralEquation = Callable[[pd.DataFrame, np.random.Generator], np.ndarray]


@dataclass
class StructuralCausalModel:
    """A lightweight structural causal model over tabular events."""

    equations: dict[str, StructuralEquation] = field(default_factory=dict)
    seed: int = 17

    def add_equation(self, variable: str, equation: StructuralEquation) -> "StructuralCausalModel":
        self.equations[variable] = equation
        return self

    def simulate(self, base: pd.DataFrame, interventions: dict[str, float] | None = None) -> pd.DataFrame:
        rng = np.random.default_rng(self.seed)
        out = base.copy()
        interventions = interventions or {}
        for key, value in interventions.items():
            out[key] = value
        for variable, equation in self.equations.items():
            if variable in interventions:
                continue
            out[variable] = equation(out, rng)
        return out


def default_lcp_scm() -> StructuralCausalModel:
    """Return structural equations consistent with the synthetic benchmark."""

    scm = StructuralCausalModel(seed=17)

    def lcp(df: pd.DataFrame, rng: np.random.Generator) -> np.ndarray:
        return (
            1450
            + 2.6 * df["network_rtt_ms"]
            + 0.72 * df["js_kb"]
            + 0.54 * df["image_kb"]
            + 130 * df["device_mobile"]
            + 85 * df["traffic_paid"]
            + 120 * df["route_complexity"]
            + 80 * df["personalization_score"]
            - 120 * df["edge_cache_enabled"]
            - 85 * df.get("image_optimization_enabled", 0)
            + rng.normal(0, 95, len(df))
        )

    scm.add_equation("lcp_ms", lcp)
    return scm
