"""Rollout policy helpers."""

from __future__ import annotations

from dataclasses import dataclass

from rt_cinfer_web.abtest.counterfactual import CounterfactualResult


@dataclass(frozen=True)
class RolloutDecision:
    stage: str
    traffic_fraction: float
    reason: str


def conservative_rollout_policy(result: CounterfactualResult, min_delta: float = 25.0) -> RolloutDecision:
    """Map a counterfactual result into a staged rollout suggestion."""

    if result.estimated_delta < -2 * min_delta:
        return RolloutDecision("pilot", 0.10, "Large simulated benefit; start with a guarded 10% pilot.")
    if result.estimated_delta < -min_delta:
        return RolloutDecision("canary", 0.02, "Moderate simulated benefit; begin with a 2% canary.")
    return RolloutDecision("hold", 0.0, "Simulated effect is not large enough for rollout.")
