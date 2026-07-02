"""Practical identifiability checks for the default web-vitals SCM."""

from __future__ import annotations

from dataclasses import dataclass

from rt_cinfer_web.scm.graph import CausalGraph


@dataclass(frozen=True)
class IdentificationResult:
    identifiable: bool
    adjustment_set: tuple[str, ...]
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "identifiable": self.identifiable,
            "adjustment_set": self.adjustment_set,
            "reasons": self.reasons,
        }


def backdoor_adjustment_check(
    graph: CausalGraph,
    treatment: str,
    outcome: str,
    observed_covariates: tuple[str, ...],
) -> IdentificationResult:
    """Return a conservative adjustment-set check.

    This is not a full do-calculus engine. It is a transparent guardrail for the
    default DAG: all observed common causes of treatment and outcome must be in
    the adjustment set, and no descendant of treatment should be adjusted for.
    """

    observed = set(observed_covariates)
    treatment_parents = graph.parents(treatment)
    outcome_ancestors = graph.ancestors(outcome)
    common_causes = tuple(sorted((treatment_parents & outcome_ancestors) - {treatment}))
    descendants = graph.descendants(treatment)
    missing = tuple(sorted(set(common_causes) - observed))
    bad_controls = tuple(sorted(observed & descendants))
    reasons: list[str] = []
    if missing:
        reasons.append(f"Missing common causes in adjustment set: {missing}.")
    if bad_controls:
        reasons.append(f"Adjustment set includes post-treatment descendants: {bad_controls}.")
    if not reasons:
        reasons.append("Observed covariates block the default backdoor paths.")
    return IdentificationResult(
        identifiable=not missing and not bad_controls,
        adjustment_set=tuple(sorted(observed)),
        reasons=tuple(reasons),
    )


def overlap_check(treated_fraction: float, lower: float = 0.02, upper: float = 0.98) -> bool:
    return lower <= treated_fraction <= upper
