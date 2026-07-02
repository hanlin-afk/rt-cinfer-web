"""Shared configuration objects."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FeatureSchema:
    """Columns used by causal estimators and web-vitals modules."""

    context_features: tuple[str, ...] = (
        "device_mobile",
        "traffic_paid",
        "region_west",
        "network_rtt_ms",
        "js_kb",
        "image_kb",
        "route_complexity",
        "personalization_score",
        "hour_sin",
        "hour_cos",
    )
    treatment: str = "edge_cache_enabled"
    outcome: str = "lcp_ms"
    timestamp: str = "timestamp"
    segment: str = "segment"


@dataclass(frozen=True)
class EstimatorConfig:
    """Configuration for the online doubly robust estimator."""

    learning_rate: float = 0.02
    l2: float = 1e-4
    propensity_clip: float = 0.05
    min_overlap: float = 0.02
    min_samples: int = 500
    max_history: int = 20_000
    confidence: float = 0.95
    stabilize_features: bool = True


@dataclass(frozen=True)
class RecommendationGateConfig:
    """Rules for turning estimates into intervention recommendations."""

    min_samples: int = 800
    min_abs_effect_ms: float = 25.0
    max_ci_width_ms: float = 180.0
    require_identifiable: bool = True
    require_no_active_drift: bool = False
    allowed_metrics: tuple[str, ...] = ("lcp_ms", "fid_ms", "cls")


@dataclass(frozen=True)
class BenchmarkConfig:
    """Synthetic benchmark configuration."""

    n_events: int = 10_000
    batch_size: int = 250
    seed: int = 13
    drift_at: int | None = 5_000
    feature_schema: FeatureSchema = field(default_factory=FeatureSchema)
