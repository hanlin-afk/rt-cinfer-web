"""Intervention definitions and recommendation objects."""

from __future__ import annotations

from dataclasses import dataclass

from rt_cinfer_web.estimators.online_dr import CausalEstimate


@dataclass(frozen=True)
class Intervention:
    name: str
    treatment_column: str
    target_metric: str
    description: str
    expected_direction: str = "decrease"
    operational_risk: str = "medium"


DEFAULT_INTERVENTIONS: tuple[Intervention, ...] = (
    Intervention(
        name="Edge cache enablement",
        treatment_column="edge_cache_enabled",
        target_metric="lcp_ms",
        description="Serve eligible page assets from an edge cache or CDN point of presence.",
        operational_risk="low",
    ),
    Intervention(
        name="Image optimization",
        treatment_column="image_optimization_enabled",
        target_metric="lcp_ms",
        description="Compress and resize product imagery before rendering.",
        operational_risk="low",
    ),
    Intervention(
        name="JavaScript deferral",
        treatment_column="js_deferral_enabled",
        target_metric="fid_ms",
        description="Defer non-critical JavaScript work to reduce input delay.",
        operational_risk="medium",
    ),
    Intervention(
        name="Layout reserve boxes",
        treatment_column="layout_reserve_enabled",
        target_metric="cls",
        description="Reserve product-card and ad-slot layout boxes before asynchronous content loads.",
        operational_risk="low",
    ),
)


@dataclass(frozen=True)
class InterventionRecommendation:
    intervention: Intervention
    estimate: CausalEstimate
    decision: str
    rationale: str
    uncertainty_note: str

    def as_dict(self) -> dict[str, object]:
        return {
            "intervention": self.intervention.name,
            "treatment_column": self.intervention.treatment_column,
            "target_metric": self.intervention.target_metric,
            "decision": self.decision,
            "rationale": self.rationale,
            "uncertainty_note": self.uncertainty_note,
            "estimate": self.estimate.as_dict(),
        }
