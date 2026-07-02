"""End-to-end real-time causal inference pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from rt_cinfer_web.abtest.counterfactual import CounterfactualABSimulator, CounterfactualResult
from rt_cinfer_web.config import EstimatorConfig, FeatureSchema, RecommendationGateConfig
from rt_cinfer_web.estimators.online_dr import CausalEstimate, OnlineDoublyRobustEstimator
from rt_cinfer_web.scm.graph import default_web_vitals_graph
from rt_cinfer_web.scm.identifiability import IdentificationResult, backdoor_adjustment_check
from rt_cinfer_web.scm.structural import default_lcp_scm
from rt_cinfer_web.streaming.drift import PageHinkleyDetector, PopulationStabilityIndex
from rt_cinfer_web.streaming.state import StreamState
from rt_cinfer_web.uncertainty.calibration import UncertaintyGate
from rt_cinfer_web.web_vitals.bottleneck import bottleneck_summary
from rt_cinfer_web.web_vitals.interventions import (
    DEFAULT_INTERVENTIONS,
    Intervention,
    InterventionRecommendation,
)
from rt_cinfer_web.web_vitals.metrics import summarize_vitals


@dataclass(frozen=True)
class PipelineConfig:
    metric: str = "lcp_ms"
    treatment: str = "edge_cache_enabled"
    features: FeatureSchema = field(default_factory=FeatureSchema)
    estimator: EstimatorConfig = field(default_factory=EstimatorConfig)
    gate: RecommendationGateConfig = field(default_factory=RecommendationGateConfig)


@dataclass(frozen=True)
class PipelineReport:
    estimate: CausalEstimate
    identification: IdentificationResult
    vital_summary: dict[str, dict[str, float | str]]
    drift_flags: dict[str, bool]
    bottlenecks: list[dict[str, float | str]]
    recommendations: list[InterventionRecommendation]
    counterfactual: CounterfactualResult | None

    def as_dict(self) -> dict[str, object]:
        return {
            "estimate": self.estimate.as_dict(),
            "identification": self.identification.as_dict(),
            "vital_summary": self.vital_summary,
            "drift_flags": self.drift_flags,
            "bottlenecks": self.bottlenecks,
            "recommendations": [r.as_dict() for r in self.recommendations],
            "counterfactual": self.counterfactual.as_dict() if self.counterfactual else None,
        }


@dataclass
class RealTimeCausalPipeline:
    """Coordinate SCM checks, streaming estimation, drift, and recommendations."""

    config: PipelineConfig = field(default_factory=PipelineConfig)
    interventions: tuple[Intervention, ...] = DEFAULT_INTERVENTIONS

    def __post_init__(self) -> None:
        feature_cols = self.config.features.context_features
        graph = default_web_vitals_graph(metric=self.config.metric, treatment=self.config.treatment)
        self.identification = backdoor_adjustment_check(
            graph,
            treatment=self.config.treatment,
            outcome=self.config.metric,
            observed_covariates=feature_cols,
        )
        self.estimator = OnlineDoublyRobustEstimator(
            features=feature_cols,
            treatment=self.config.treatment,
            outcome=self.config.metric,
            config=self.config.estimator,
            identifiable_assumption=self.identification.identifiable,
        )
        self.gate = UncertaintyGate(self.config.gate)
        self.state = StreamState()
        self.lcp_drift = PageHinkleyDetector(threshold=250.0)
        self.psi_rtt = PopulationStabilityIndex(feature="network_rtt_ms")
        self.cf_simulator = CounterfactualABSimulator(default_lcp_scm())

    def update(self, batch: pd.DataFrame) -> PipelineReport:
        self.state.update_counts(len(batch))
        estimate = self.estimator.update(batch)
        lcp_drift_flag = self.lcp_drift.update(batch[self.config.metric].astype(float).to_numpy())
        _, rtt_drift_flag = self.psi_rtt.update(batch)
        self.state.active_drift_flags = {
            "metric_page_hinkley": bool(lcp_drift_flag),
            "network_rtt_psi": bool(rtt_drift_flag),
        }
        active_drift = any(self.state.active_drift_flags.values())

        recommendations: list[InterventionRecommendation] = []
        main_intervention = next(
            (
                item
                for item in self.interventions
                if item.treatment_column == self.config.treatment and item.target_metric == self.config.metric
            ),
            Intervention(
                name=self.config.treatment,
                treatment_column=self.config.treatment,
                target_metric=self.config.metric,
                description="Configured intervention.",
            ),
        )
        recommendations.append(self.gate.evaluate(main_intervention, estimate, active_drift=active_drift))

        counterfactual = None
        if self.config.metric == "lcp_ms":
            counterfactual = self.cf_simulator.simulate_binary_intervention(
                batch, treatment=self.config.treatment, metric=self.config.metric, set_to=1
            )

        report = PipelineReport(
            estimate=estimate,
            identification=self.identification,
            vital_summary=summarize_vitals(batch),
            drift_flags=self.state.active_drift_flags,
            bottlenecks=bottleneck_summary(batch),
            recommendations=recommendations,
            counterfactual=counterfactual,
        )
        return report
