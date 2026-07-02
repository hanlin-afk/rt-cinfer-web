"""Counterfactual rollout simulation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from rt_cinfer_web.scm.structural import StructuralCausalModel


@dataclass(frozen=True)
class CounterfactualResult:
    intervention: str
    metric: str
    baseline_mean: float
    counterfactual_mean: float
    estimated_delta: float
    n: int

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "intervention": self.intervention,
            "metric": self.metric,
            "baseline_mean": self.baseline_mean,
            "counterfactual_mean": self.counterfactual_mean,
            "estimated_delta": self.estimated_delta,
            "n": self.n,
        }


@dataclass
class CounterfactualABSimulator:
    """Pre-rollout simulator based on structural equations."""

    scm: StructuralCausalModel

    def simulate_binary_intervention(
        self,
        recent_batch: pd.DataFrame,
        treatment: str,
        metric: str,
        set_to: int = 1,
    ) -> CounterfactualResult:
        baseline = recent_batch.copy()
        counterfactual = self.scm.simulate(baseline, interventions={treatment: set_to})
        baseline_mean = float(np.mean(baseline[metric].astype(float)))
        counterfactual_mean = float(np.mean(counterfactual[metric].astype(float)))
        return CounterfactualResult(
            intervention=f"do({treatment}={set_to})",
            metric=metric,
            baseline_mean=baseline_mean,
            counterfactual_mean=counterfactual_mean,
            estimated_delta=counterfactual_mean - baseline_mean,
            n=len(recent_batch),
        )
