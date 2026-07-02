#!/usr/bin/env python
"""Fetch real public Web Vitals field data from PageSpeed Insights / CrUX.

Example:
    python scripts/fetch_pagespeed_crux.py \
      --origins configs/us_ecommerce_origins.csv \
      --out data/real/public_crux_pagespeed.csv \
      --raw-dir data/real/raw_pagespeed

Set PAGESPEED_API_KEY for higher-volume repeatable runs.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from rt_cinfer_web.data.public_web_vitals import PageSpeedCrUXClient, load_origins_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch public CrUX field data through PageSpeed Insights")
    parser.add_argument("--origins", default="configs/us_ecommerce_origins.csv")
    parser.add_argument("--out", default="data/real/public_crux_pagespeed.csv")
    parser.add_argument("--raw-dir", default="data/real/raw_pagespeed")
    parser.add_argument("--strategies", nargs="+", default=["mobile", "desktop"])
    parser.add_argument("--sleep-seconds", type=float, default=1.0)
    parser.add_argument("--api-key-env", default="PAGESPEED_API_KEY")
    args = parser.parse_args()

    origins = load_origins_csv(args.origins)
    api_key = os.environ.get(args.api_key_env)
    client = PageSpeedCrUXClient(api_key=api_key, sleep_seconds=args.sleep_seconds)
    df = client.fetch_many(origins, strategies=tuple(args.strategies), raw_dir=args.raw_dir)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} public field-data rows to {args.out}")
    print("Raw API responses are preserved for auditability in", args.raw_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
