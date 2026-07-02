# Real Public Data Extension

RT-CInfer-Web supports two evidence modes:

1. **Synthetic benchmark mode** for validating algorithms when the ground-truth treatment effect is known.
2. **Real public observational mode** for analyzing public Web Vitals field data from Google CrUX / PageSpeed Insights and optional HTTP Archive joins.

## Why CrUX / PageSpeed Insights

Google's Chrome UX Report (CrUX) is the public dataset behind the Web Vitals program. It provides anonymized, representative real-user experience data for public origins and URLs with enough traffic. PageSpeed Insights exposes CrUX field data, including metrics such as LCP, INP, CLS, FCP, and TTFB when available.

## Why HTTP Archive

HTTP Archive tracks how the web is built and publishes crawl-level page construction data through reports and BigQuery. Its Core Web Vitals Technology Report combines real-user CrUX data with technology detections from HTTP Archive, which makes it useful for web-infrastructure research.

## Metric note: FID versus INP

The original project proposal mentions FID. For modern 2026 Web Vitals work, the repository supports both legacy `fid_ms` and current `inp_ms` because Google replaced FID with INP as the Core Web Vital for responsiveness in March 2024. The public-data scripts therefore prefer INP when available and retain FID fields only for legacy data.

## What the public-data results can honestly claim

Public CrUX/PSI data can support statements like:

- The project can ingest real public Web Vitals field data.
- The code preserves data provenance and raw API responses.
- The analysis identifies public-origin performance bottlenecks and uncertainty boundaries.
- The public-data workflow is reproducible by another reviewer with the same origin list and API access.

Public data alone should not be used to claim:

- private Walmart/Amazon/Target deployment;
- production adoption by any company;
- verified revenue improvement;
- a causal effect of a real intervention without a documented rollout, A/B test, or quasi-experimental identification design.

## Reproducible workflow

```bash
python -m pip install -e ".[dev]"
python scripts/fetch_pagespeed_crux.py --origins configs/us_ecommerce_origins.csv
python scripts/run_real_public_observational.py --input data/real/public_crux_pagespeed.csv
```

For weekly time series, use `scripts/fetch_crux_history_template.py` after setting `CRUX_API_KEY`.

## Causal workflow with a real intervention log

If you have a real dated intervention log, create a CSV with columns such as:

```text
origin,intervention_name,rollout_start_date,rollout_end_date,treatment_share,notes
```

Then join it with CrUX History API weekly rows and run an event-study or difference-in-differences analysis. The repository does not fabricate such a log.
