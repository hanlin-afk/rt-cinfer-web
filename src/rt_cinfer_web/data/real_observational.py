"""Utilities for analyzing real public Web Vitals observations.

These utilities operate on public, origin-level observations. They are useful
for factual external validity checks and bottleneck screening, but they do not
claim private deployment performance or definitive causal effects without an
intervention log or randomization/identification strategy.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from rt_cinfer_web.web_vitals.metrics import classify_metric


@dataclass(frozen=True)
class ObservationalStudySummary:
    n_rows: int
    n_origins: int
    generated_at_note: str
    metric_summary: dict[str, dict[str, float | str | int]]
    identifiability_note: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "n_rows": self.n_rows,
            "n_origins": self.n_origins,
            "generated_at_note": self.generated_at_note,
            "metric_summary": self.metric_summary,
            "identifiability_note": self.identifiability_note,
        }


PUBLIC_METRICS = {
    "lcp_p75_ms": "lcp_ms",
    "inp_p75_ms": "inp_ms",
    "fid_p75_ms": "fid_ms",
    "cls_p75": "cls",
    "fcp_p75_ms": "fcp_ms",
    "ttfb_p75_ms": "ttfb_ms",
}


def summarize_public_vitals(df: pd.DataFrame) -> ObservationalStudySummary:
    metrics: dict[str, dict[str, float | str | int]] = {}
    for source_col, canonical_metric in PUBLIC_METRICS.items():
        if source_col not in df.columns:
            continue
        values = pd.to_numeric(df[source_col], errors="coerce").dropna()
        if values.empty:
            continue
        p75 = float(np.quantile(values, 0.75))
        row: dict[str, float | str | int] = {
            "n": int(values.shape[0]),
            "mean": float(values.mean()),
            "median": float(values.median()),
            "p75_across_origins": p75,
            "p90_across_origins": float(np.quantile(values, 0.90)),
        }
        if canonical_metric in {"lcp_ms", "fid_ms", "inp_ms", "cls"}:
            row["status_at_cross_origin_p75"] = classify_metric(canonical_metric, p75)
        metrics[source_col] = row

    return ObservationalStudySummary(
        n_rows=int(len(df)),
        n_origins=int(df["origin"].nunique()) if "origin" in df.columns else 0,
        generated_at_note="Computed from normalized public CrUX/PageSpeed records supplied to this script.",
        metric_summary=metrics,
        identifiability_note=(
            "This is real public observational data. It supports external-validity and bottleneck screening. "
            "It should not be described as a verified causal deployment result unless joined with a real "
            "intervention log, randomized rollout, or other defensible identification design."
        ),
    )


def write_markdown_report(summary: ObservationalStudySummary, output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Real Public Web Vitals Observational Report",
        "",
        f"Rows analyzed: **{summary.n_rows}**",
        f"Unique origins: **{summary.n_origins}**",
        "",
        "## Metric summary",
        "",
        "| Metric | n | mean | median | p75 across origins | p90 across origins | status |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for metric, stats in summary.metric_summary.items():
        lines.append(
            "| {metric} | {n} | {mean:.3f} | {median:.3f} | {p75:.3f} | {p90:.3f} | {status} |".format(
                metric=metric,
                n=int(stats.get("n", 0)),
                mean=float(stats.get("mean", 0.0)),
                median=float(stats.get("median", 0.0)),
                p75=float(stats.get("p75_across_origins", 0.0)),
                p90=float(stats.get("p90_across_origins", 0.0)),
                status=str(stats.get("status_at_cross_origin_p75", "not_classified")),
            )
        )
    lines.extend([
        "",
        "## Identification boundary",
        "",
        summary.identifiability_note,
        "",
        "## Recommended next step for causal claims",
        "",
        "Join these public observations with a documented intervention log, such as a dated CDN-cache rollout, image-optimization rollout, JavaScript-splitting rollout, or server-region change. Then run an event-study or difference-in-differences design and report assumptions, falsification checks, and uncertainty intervals.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
