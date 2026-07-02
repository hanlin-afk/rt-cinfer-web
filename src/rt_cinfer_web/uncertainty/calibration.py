"""Decision calibration for intervention recommendations."""

from __future__ import annotations

from dataclasses import dataclass

from rt_cinfer_web.config import RecommendationGateConfig
from rt_cinfer_web.estimators.online_dr import CausalEstimate
from rt_cinfer_web.web_vitals.interventions import Intervention, InterventionRecommendation


@dataclass
class UncertaintyGate:
    """Convert causal estimates into conservative operational decisions."""

    config: RecommendationGateConfig = RecommendationGateConfig()

    def evaluate(
        self,
        intervention: Intervention,
        estimate: CausalEstimate,
        active_drift: bool = False,
    ) -> InterventionRecommendation:
        ci_width = estimate.ci_high - estimate.ci_low
        reasons: list[str] = []
        decision = "hold"
        if estimate.outcome not in self.config.allowed_metrics:
            reasons.append(f"Metric {estimate.outcome} is not configured for automated recommendations.")
        if self.config.require_identifiable and not estimate.identifiable:
            reasons.append("Causal effect is not currently identifiable under the configured gate.")
        if estimate.n < self.config.min_samples:
            reasons.append(f"Sample size {estimate.n} is below gate minimum {self.config.min_samples}.")
        if ci_width > self.config.max_ci_width_ms and estimate.outcome != "cls":
            reasons.append(f"Confidence interval width {ci_width:.1f} is too wide.")
        if self.config.require_no_active_drift and active_drift:
            reasons.append("Active drift detected; waiting for adaptation before recommending rollout.")
        if abs(estimate.ate) < self.config.min_abs_effect_ms and estimate.outcome != "cls":
            reasons.append("Estimated effect is too small for operational action.")
        if not reasons and estimate.ci_high < 0:
            decision = "recommend"
            reasons.append("Confidence interval is entirely below zero; intervention is estimated to improve latency.")
        elif not reasons:
            reasons.append("Uncertainty interval crosses zero; intervention remains under observation.")
        uncertainty_note = f"ATE={estimate.ate:.3f}, CI=[{estimate.ci_low:.3f}, {estimate.ci_high:.3f}], n={estimate.n}."
        return InterventionRecommendation(
            intervention=intervention,
            estimate=estimate,
            decision=decision,
            rationale=" ".join(reasons),
            uncertainty_note=uncertainty_note,
        )
