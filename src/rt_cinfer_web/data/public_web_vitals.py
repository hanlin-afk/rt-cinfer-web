"""Public real-data adapters for Core Web Vitals research.

The adapters in this module retrieve or normalize public field data from
Google's Chrome UX Report (CrUX) surfaces. They intentionally keep raw JSON
responses and provenance metadata so downstream reports can distinguish real
public observations from synthetic benchmarks and from private production RUM.
"""

from __future__ import annotations

import csv
import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


@dataclass(frozen=True)
class PublicVitalsRecord:
    """Normalized origin-level public Web Vitals observation."""

    origin: str
    strategy: str
    fetched_at_utc: str
    source: str
    source_url: str
    form_factor: str | None = None
    collection_period: str | None = None
    lcp_p75_ms: float | None = None
    inp_p75_ms: float | None = None
    fid_p75_ms: float | None = None
    cls_p75: float | None = None
    fcp_p75_ms: float | None = None
    ttfb_p75_ms: float | None = None
    lcp_category: str | None = None
    inp_category: str | None = None
    fid_category: str | None = None
    cls_category: str | None = None
    overall_category: str | None = None
    lighthouse_performance_score: float | None = None
    notes: str = "public CrUX field data; not private production telemetry"

    def as_dict(self) -> dict[str, Any]:
        return {
            "origin": self.origin,
            "strategy": self.strategy,
            "fetched_at_utc": self.fetched_at_utc,
            "source": self.source,
            "source_url": self.source_url,
            "form_factor": self.form_factor,
            "collection_period": self.collection_period,
            "lcp_p75_ms": self.lcp_p75_ms,
            "inp_p75_ms": self.inp_p75_ms,
            "fid_p75_ms": self.fid_p75_ms,
            "cls_p75": self.cls_p75,
            "fcp_p75_ms": self.fcp_p75_ms,
            "ttfb_p75_ms": self.ttfb_p75_ms,
            "lcp_category": self.lcp_category,
            "inp_category": self.inp_category,
            "fid_category": self.fid_category,
            "cls_category": self.cls_category,
            "overall_category": self.overall_category,
            "lighthouse_performance_score": self.lighthouse_performance_score,
            "notes": self.notes,
        }


METRIC_MAP = {
    "LARGEST_CONTENTFUL_PAINT_MS": "lcp_p75_ms",
    "INTERACTION_TO_NEXT_PAINT": "inp_p75_ms",
    "FIRST_INPUT_DELAY_MS": "fid_p75_ms",
    "CUMULATIVE_LAYOUT_SHIFT_SCORE": "cls_p75",
    "FIRST_CONTENTFUL_PAINT_MS": "fcp_p75_ms",
    "EXPERIMENTAL_TIME_TO_FIRST_BYTE": "ttfb_p75_ms",
}

CATEGORY_MAP = {
    "LARGEST_CONTENTFUL_PAINT_MS": "lcp_category",
    "INTERACTION_TO_NEXT_PAINT": "inp_category",
    "FIRST_INPUT_DELAY_MS": "fid_category",
    "CUMULATIVE_LAYOUT_SHIFT_SCORE": "cls_category",
}


def _metric_percentile(metric_payload: dict[str, Any]) -> float | None:
    percentile = metric_payload.get("percentile")
    if percentile is None:
        return None
    try:
        return float(percentile)
    except (TypeError, ValueError):
        return None


def _read_origin_list(path: str | Path) -> list[str]:
    rows: list[str] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            origin = (row.get("origin") or "").strip()
            if origin:
                rows.append(origin)
    return rows


class PageSpeedCrUXClient:
    """Fetch public CrUX field data exposed by the PageSpeed Insights API.

    PageSpeed Insights returns CrUX field data when an origin or URL has enough
    representative, anonymized samples. API keys are optional for low-volume use
    but recommended for repeatable research runs.
    """

    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    def __init__(self, api_key: str | None = None, timeout_seconds: int = 60, sleep_seconds: float = 1.0):
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.sleep_seconds = sleep_seconds

    def build_url(self, origin: str, strategy: str = "mobile") -> str:
        params = {
            "url": origin,
            "strategy": strategy,
            "category": "performance",
        }
        if self.api_key:
            params["key"] = self.api_key
        return f"{self.endpoint}?{urllib.parse.urlencode(params)}"

    def fetch_one(self, origin: str, strategy: str = "mobile") -> dict[str, Any]:
        url = self.build_url(origin, strategy=strategy)
        request = urllib.request.Request(url, headers={"User-Agent": "rt-cinfer-web/0.2"})
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload

    def normalize(self, origin: str, strategy: str, payload: dict[str, Any], source_url: str) -> PublicVitalsRecord:
        loading = payload.get("loadingExperience") or payload.get("originLoadingExperience") or {}
        metrics = loading.get("metrics", {})
        row: dict[str, Any] = {}
        for api_name, output_name in METRIC_MAP.items():
            if api_name in metrics:
                row[output_name] = _metric_percentile(metrics[api_name])
        for api_name, output_name in CATEGORY_MAP.items():
            if api_name in metrics:
                row[output_name] = metrics[api_name].get("category")

        lighthouse_score = None
        lighthouse = payload.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})
        performance = categories.get("performance", {})
        if performance.get("score") is not None:
            lighthouse_score = float(performance["score"])

        period = None
        if loading.get("collectionPeriod"):
            period = json.dumps(loading["collectionPeriod"], sort_keys=True)

        return PublicVitalsRecord(
            origin=origin,
            strategy=strategy,
            fetched_at_utc=str(payload.get("analysisUTCTimestamp") or ""),
            source="PageSpeed Insights API / Chrome UX Report field data",
            source_url=source_url,
            form_factor=loading.get("formFactor"),
            collection_period=period,
            overall_category=loading.get("overall_category"),
            lighthouse_performance_score=lighthouse_score,
            **row,
        )

    def fetch_many(
        self,
        origins: Iterable[str],
        strategies: tuple[str, ...] = ("mobile", "desktop"),
        raw_dir: str | Path | None = None,
    ) -> pd.DataFrame:
        records: list[dict[str, Any]] = []
        raw_path = Path(raw_dir) if raw_dir else None
        if raw_path:
            raw_path.mkdir(parents=True, exist_ok=True)

        for origin in origins:
            for strategy in strategies:
                url = self.build_url(origin, strategy=strategy)
                payload = self.fetch_one(origin, strategy=strategy)
                normalized = self.normalize(origin, strategy, payload, source_url=url)
                records.append(normalized.as_dict())
                if raw_path:
                    safe = origin.replace("https://", "").replace("http://", "").replace("/", "_")
                    (raw_path / f"{safe}_{strategy}.json").write_text(
                        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
                    )
                time.sleep(self.sleep_seconds)
        return pd.DataFrame(records)


def load_origins_csv(path: str | Path) -> list[str]:
    """Load a CSV file with an `origin` column."""

    return _read_origin_list(path)
