"""Core Web Vitals thresholds and summaries."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class VitalThreshold:
    good: float
    needs_improvement: float
    lower_is_better: bool = True


THRESHOLDS: dict[str, VitalThreshold] = {
    "lcp_ms": VitalThreshold(good=2500, needs_improvement=4000),
    "inp_ms": VitalThreshold(good=200, needs_improvement=500),
    "fid_ms": VitalThreshold(good=100, needs_improvement=300),
    "cls": VitalThreshold(good=0.1, needs_improvement=0.25),
}


def classify_metric(metric: str, value: float) -> str:
    threshold = THRESHOLDS[metric]
    if value <= threshold.good:
        return "good"
    if value <= threshold.needs_improvement:
        return "needs_improvement"
    return "poor"


def summarize_vitals(
    df: pd.DataFrame, metrics: tuple[str, ...] = ("lcp_ms", "inp_ms", "fid_ms", "cls")
) -> dict[str, dict[str, float | str]]:
    summary: dict[str, dict[str, float | str]] = {}
    for metric in metrics:
        if metric not in df.columns:
            continue
        values = df[metric].astype(float).dropna().to_numpy()
        if values.size == 0:
            continue
        p75 = float(np.quantile(values, 0.75))
        summary[metric] = {
            "mean": float(np.mean(values)),
            "p50": float(np.quantile(values, 0.50)),
            "p75": p75,
            "p95": float(np.quantile(values, 0.95)),
            "status_at_p75": classify_metric(metric, p75),
        }
    return summary
