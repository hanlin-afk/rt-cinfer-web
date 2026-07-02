"""Bottleneck localization for web-vitals events."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BottleneckSignal:
    name: str
    score: float
    evidence: str


def localize_lcp_bottlenecks(batch: pd.DataFrame) -> list[BottleneckSignal]:
    """Rank likely LCP bottlenecks from transparent feature scores."""

    lcp = batch["lcp_ms"].astype(float).to_numpy()
    signals: list[BottleneckSignal] = []
    feature_map = {
        "network": "network_rtt_ms",
        "javascript": "js_kb",
        "images": "image_kb",
        "route_complexity": "route_complexity",
        "personalization": "personalization_score",
    }
    for name, col in feature_map.items():
        x = batch[col].astype(float).to_numpy()
        corr = float(np.corrcoef(x, lcp)[0, 1]) if np.std(x) > 0 and np.std(lcp) > 0 else 0.0
        signals.append(
            BottleneckSignal(
                name=name,
                score=abs(corr),
                evidence=f"absolute correlation with LCP in recent batch: {abs(corr):.3f}",
            )
        )
    return sorted(signals, key=lambda s: s.score, reverse=True)


def bottleneck_summary(batch: pd.DataFrame, top_k: int = 3) -> list[dict[str, float | str]]:
    return [s.__dict__ for s in localize_lcp_bottlenecks(batch)[:top_k]]
