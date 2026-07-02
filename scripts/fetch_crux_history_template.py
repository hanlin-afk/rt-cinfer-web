#!/usr/bin/env python
"""Template for fetching CrUX History API time series.

This script is intentionally kept as a template because the CrUX History API
requires a Google API key. It stores raw JSON and normalized weekly p75 values
when the key is provided through CRUX_API_KEY.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ENDPOINT = "https://chromeuxreport.googleapis.com/v1/records:queryHistoryRecord"
METRICS = {
    "largest_contentful_paint": "lcp_p75_ms",
    "interaction_to_next_paint": "inp_p75_ms",
    "cumulative_layout_shift": "cls_p75",
    "first_contentful_paint": "fcp_p75_ms",
    "experimental_time_to_first_byte": "ttfb_p75_ms",
}


def read_origins(path: str) -> list[str]:
    with open(path, newline="", encoding="utf-8") as handle:
        return [row["origin"] for row in csv.DictReader(handle) if row.get("origin")]


def fetch_history(origin: str, api_key: str, collection_period_count: int) -> dict[str, Any]:
    url = f"{ENDPOINT}?{urllib.parse.urlencode({'key': api_key})}"
    payload = json.dumps({"origin": origin, "collectionPeriodCount": collection_period_count}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "rt-cinfer-web/0.2"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_history(origin: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    record = payload.get("record", {})
    collection_periods = record.get("collectionPeriods", [])
    metrics = record.get("metrics", {})
    rows: list[dict[str, Any]] = []
    for idx, period in enumerate(collection_periods):
        row: dict[str, Any] = {
            "origin": origin,
            "period_index": idx,
            "first_date": period.get("firstDate"),
            "last_date": period.get("lastDate"),
            "source": "Chrome UX Report History API",
        }
        for api_metric, col in METRICS.items():
            series = metrics.get(api_metric, {}).get("percentilesTimeseries", {}).get("p75s", [])
            if idx < len(series):
                row[col] = series[idx]
        rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch CrUX History API weekly origin-level time series")
    parser.add_argument("--origins", default="configs/us_ecommerce_origins.csv")
    parser.add_argument("--out", default="data/real/public_crux_history.csv")
    parser.add_argument("--raw-dir", default="data/real/raw_crux_history")
    parser.add_argument("--collection-period-count", type=int, default=40)
    parser.add_argument("--sleep-seconds", type=float, default=1.0)
    args = parser.parse_args()

    api_key = os.environ.get("CRUX_API_KEY")
    if not api_key:
        raise SystemExit("Set CRUX_API_KEY before running this script.")

    raw_dir = Path(args.raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict[str, Any]] = []
    for origin in read_origins(args.origins):
        payload = fetch_history(origin, api_key, args.collection_period_count)
        safe = origin.replace("https://", "").replace("http://", "").replace("/", "_")
        (raw_dir / f"{safe}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        all_rows.extend(normalize_history(origin, payload))
        time.sleep(args.sleep_seconds)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    if all_rows:
        with open(args.out, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=sorted({key for row in all_rows for key in row}))
            writer.writeheader()
            writer.writerows(all_rows)
    print(f"Wrote {len(all_rows)} weekly public CrUX rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
