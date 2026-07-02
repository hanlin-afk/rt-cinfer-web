"""Synthetic streaming data for web-vitals causal inference.

The generator intentionally creates confounding: high-complexity pages and paid
traffic are more likely to receive interventions, while also having worse Web
Vitals. This lets tests check whether the doubly robust estimator improves over
simple treated-control differences.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

import numpy as np
import pandas as pd

from rt_cinfer_web.utils import sigmoid


@dataclass(frozen=True)
class GroundTruthEffects:
    """Known synthetic causal effects for validation."""

    edge_cache_lcp_ms: float = -120.0
    image_optimization_lcp_ms: float = -85.0
    js_deferral_fid_ms: float = -18.0
    layout_reserve_cls: float = -0.035


@dataclass
class SyntheticWebVitalsStream:
    """Generate streaming e-commerce web-vitals events.

    Parameters
    ----------
    seed:
        Random seed for deterministic reproduction.
    drift_at:
        Event index at which the user population shifts. ``None`` disables drift.
    ground_truth:
        Known synthetic treatment effects.
    """

    seed: int = 13
    drift_at: int | None = 5_000
    ground_truth: GroundTruthEffects = GroundTruthEffects()

    def generate(self, n_events: int = 10_000) -> pd.DataFrame:
        rng = np.random.default_rng(self.seed)
        idx = np.arange(n_events)
        after_drift = np.zeros(n_events, dtype=float)
        if self.drift_at is not None:
            after_drift = (idx >= self.drift_at).astype(float)

        hour = idx % 24
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)

        device_mobile = rng.binomial(1, 0.58 + 0.12 * after_drift)
        traffic_paid = rng.binomial(1, 0.32 + 0.08 * after_drift)
        region_west = rng.binomial(1, 0.38)
        route_complexity = np.clip(rng.normal(0.0 + 0.45 * traffic_paid, 1.0, n_events), -2.0, 3.0)
        personalization_score = np.clip(rng.beta(2 + traffic_paid, 5, n_events), 0, 1)
        network_rtt_ms = np.clip(
            rng.normal(95 + 60 * device_mobile + 15 * after_drift - 8 * region_west, 24), 25, 260
        )
        js_kb = np.clip(
            rng.normal(440 + 85 * route_complexity + 70 * personalization_score, 90), 120, 980
        )
        image_kb = np.clip(rng.normal(950 + 170 * route_complexity, 180), 280, 1800)

        # Non-random intervention assignment: intentionally confounded.
        edge_logits = (
            -0.8
            + 0.9 * traffic_paid
            + 0.55 * route_complexity
            + 0.004 * network_rtt_ms
            + 0.25 * after_drift
        )
        edge_prob = sigmoid(edge_logits)
        edge_cache_enabled = rng.binomial(1, edge_prob)

        img_logits = -0.4 + 0.0025 * image_kb + 0.35 * device_mobile - 0.25 * region_west
        image_optimization_enabled = rng.binomial(1, sigmoid(img_logits))

        js_logits = -0.25 + 0.0032 * js_kb + 0.45 * route_complexity
        js_deferral_enabled = rng.binomial(1, sigmoid(js_logits))

        layout_reserve_enabled = rng.binomial(
            1, sigmoid(-0.5 + 0.55 * route_complexity + 0.4 * personalization_score)
        )

        # Potential-outcome style metric generation.
        baseline_lcp = (
            1450
            + 2.6 * network_rtt_ms
            + 0.72 * js_kb
            + 0.54 * image_kb
            + 130 * device_mobile
            + 85 * traffic_paid
            + 120 * route_complexity
            + 80 * personalization_score
            + 40 * after_drift
        )
        lcp_ms = (
            baseline_lcp
            + self.ground_truth.edge_cache_lcp_ms * edge_cache_enabled
            + self.ground_truth.image_optimization_lcp_ms * image_optimization_enabled
            + rng.normal(0, 95, n_events)
        )

        baseline_fid = (
            36
            + 0.045 * js_kb
            + 13 * device_mobile
            + 8 * route_complexity
            + 5 * traffic_paid
            + 4 * after_drift
        )
        fid_ms = (
            baseline_fid
            + self.ground_truth.js_deferral_fid_ms * js_deferral_enabled
            + rng.normal(0, 7.5, n_events)
        )

        baseline_cls = (
            0.055
            + 0.00009 * image_kb
            + 0.028 * personalization_score
            + 0.012 * device_mobile
            + 0.008 * route_complexity
        )
        cls = np.clip(
            baseline_cls + self.ground_truth.layout_reserve_cls * layout_reserve_enabled + rng.normal(0, 0.018, n_events),
            0,
            None,
        )

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2026-06-01", periods=n_events, freq="s"),
                "event_index": idx,
                "device_mobile": device_mobile,
                "traffic_paid": traffic_paid,
                "region_west": region_west,
                "network_rtt_ms": network_rtt_ms,
                "js_kb": js_kb,
                "image_kb": image_kb,
                "route_complexity": route_complexity,
                "personalization_score": personalization_score,
                "hour_sin": hour_sin,
                "hour_cos": hour_cos,
                "edge_cache_enabled": edge_cache_enabled,
                "image_optimization_enabled": image_optimization_enabled,
                "js_deferral_enabled": js_deferral_enabled,
                "layout_reserve_enabled": layout_reserve_enabled,
                "lcp_ms": lcp_ms,
                "fid_ms": np.clip(fid_ms, 0, None),
                "cls": cls,
                "segment": np.where(device_mobile == 1, "mobile", "desktop"),
                "after_drift": after_drift,
            }
        )
        return df

    def iter_batches(self, n_events: int = 10_000, batch_size: int = 250) -> Iterator[pd.DataFrame]:
        df = self.generate(n_events=n_events)
        for start in range(0, n_events, batch_size):
            yield df.iloc[start : start + batch_size].copy()


def load_sample(n_events: int = 1000, seed: int = 13) -> pd.DataFrame:
    """Convenience helper for examples and tests."""

    return SyntheticWebVitalsStream(seed=seed).generate(n_events=n_events)
