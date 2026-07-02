#!/usr/bin/env python
"""Generate a transparent report from real public Web Vitals observations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from rt_cinfer_web.data.real_observational import summarize_public_vitals, write_markdown_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze normalized public CrUX/PageSpeed field data")
    parser.add_argument("--input", default="data/real/public_crux_pagespeed.csv")
    parser.add_argument("--report", default="results/real_public_observational/report.md")
    parser.add_argument("--json", default="results/real_public_observational/summary.json")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    summary = summarize_public_vitals(df)
    write_markdown_report(summary, args.report)
    Path(args.json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json).write_text(json.dumps(summary.as_dict(), indent=2), encoding="utf-8")
    print(f"Wrote report to {args.report}")
    print(f"Wrote JSON summary to {args.json}")
    print(summary.identifiability_note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
