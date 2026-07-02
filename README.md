# RT-CInfer-Web

**Real-Time Causal Inference for U.S. E-Commerce Web Infrastructure**

RT-CInfer-Web is an open-source reference implementation for moving web-performance optimization from correlation-based heuristics to streaming causal decision support. It models Core Web Vitals such as **Largest Contentful Paint (LCP)**, **Interaction to Next Paint (INP)**, legacy **First Input Delay (FID)**, and **Cumulative Layout Shift (CLS)** with structural causal graphs, online doubly robust estimators, drift detection, counterfactual rollout simulation, and uncertainty-aware intervention recommendations.

The repository is designed as a research artifact: it is transparent, reproducible, citable, and easy for reviewers, researchers, and engineering teams to inspect. The included benchmark data is synthetic and intended for reproducible methodology validation only. The repository also includes a **real public data extension** for fetching and analyzing public CrUX/PageSpeed Web Vitals field data without presenting it as private production deployment evidence.

## What this project provides

- **Structural causal models for web infrastructure**: explicit graphs linking user context, network conditions, page composition, infrastructure choices, interventions, and Web Vitals.
- **Online doubly robust estimation**: streaming AIPW/DR estimates that combine propensity and outcome models and adapt to traffic shifts.
- **Counterfactual A/B preflight testing**: pre-rollout simulation of expected LCP/INP/FID/CLS impact under candidate interventions.
- **Calibrated uncertainty and identifiability gating**: recommendations are issued only when overlap, sample size, graph assumptions, and confidence bounds are acceptable.
- **Bottleneck localization**: separates likely front-end, network, CDN/cache, and personalization bottlenecks.
- **Reproducible synthetic benchmarks**: deterministic traffic simulation with known ground-truth treatment effects, drift, and confounding.
- **Real public Web Vitals adapters**: optional scripts for fetching origin-level CrUX/PageSpeed field data, preserving raw JSON responses, and generating transparent observational reports.
- **GitHub-ready engineering package**: tests, CLI, docs, examples, license, citation metadata, and CI workflow.

## Repository structure

```text
rt-cinfer-web/
├── src/rt_cinfer_web/          # Python package
│   ├── scm/                    # DAG, SCM, identifiability, IV checks
│   ├── estimators/             # Online doubly robust estimators
│   ├── streaming/              # Rolling windows and drift detectors
│   ├── web_vitals/             # Metrics, bottleneck localization, interventions
│   ├── uncertainty/            # Bootstrap and conformal-style calibration
│   ├── abtest/                 # Counterfactual rollout simulator
│   ├── data/                   # Synthetic stream generator
│   └── pipeline.py             # End-to-end orchestrator
├── benchmarks/                 # Reproducible benchmark runner
├── configs/                    # Public origin lists for reproducible real-data queries
├── scripts/                    # Fetch and analyze public CrUX/PageSpeed data
├── examples/                   # Quick-start and streaming examples
├── notebooks/                  # Exploratory notebook
├── docs/                       # Research protocol and theoretical framework
├── tests/                      # Unit tests
├── .github/workflows/ci.yml    # GitHub Actions CI
├── CITATION.cff                # Citation metadata
├── LICENSE                     # MIT License
└── pyproject.toml              # Package configuration
```

## Installation

```bash
git clone https://github.com/hanlin-afk/rt-cinfer-web.git
cd rt-cinfer-web
python -m pip install -e ".[dev]"
```

## Quick start

Run a deterministic synthetic streaming benchmark:

```bash
python -m rt_cinfer_web.cli benchmark --n-events 5000 --seed 7 --metric lcp_ms
```

Or from Python:

```python
from rt_cinfer_web.data.synthetic import SyntheticWebVitalsStream
from rt_cinfer_web.pipeline import RealTimeCausalPipeline, PipelineConfig

stream = SyntheticWebVitalsStream(seed=7)
pipeline = RealTimeCausalPipeline(PipelineConfig(metric="lcp_ms"))

for batch in stream.iter_batches(n_events=5000, batch_size=250):
    report = pipeline.update(batch)

print(report.estimate)
print(report.recommendations[:2])
```

A typical synthetic result estimates that enabling edge cache and image optimization reduces LCP. The exact estimate varies by seed and drift setting. Because this is a synthetic benchmark, it should not be presented as a real production deployment outcome.


## Real public data workflow

The repository can ingest real public field data from CrUX surfaces exposed through PageSpeed Insights. This supports honest statements such as: “the framework has a reproducible public-data ingestion and observational analysis pipeline.” It does **not** prove private deployment, company adoption, revenue impact, or a causal effect unless paired with a real intervention log or randomized rollout.

```bash
python scripts/fetch_pagespeed_crux.py \
  --origins configs/us_ecommerce_origins.csv \
  --out data/real/public_crux_pagespeed.csv \
  --raw-dir data/real/raw_pagespeed

python scripts/run_real_public_observational.py \
  --input data/real/public_crux_pagespeed.csv \
  --report results/real_public_observational/report.md
```

For weekly time-series analysis, use `scripts/fetch_crux_history_template.py` with `CRUX_API_KEY`. See [`docs/real_public_data.md`](docs/real_public_data.md) for the evidence boundary and recommended causal workflow.

## Causal target

For a candidate intervention \(A\), such as edge cache enablement or image compression, the primary estimand is:

\[
\tau = \mathbb{E}[Y(1) - Y(0)]
\]

where \(Y\) is a Web Vital metric such as LCP. Negative values are beneficial for latency metrics because lower LCP/INP/FID/CLS is better.

The online doubly robust score used in this reference implementation is:

\[
\psi_i = \hat{\mu}_1(X_i) - \hat{\mu}_0(X_i)
+ \frac{A_i(Y_i - \hat{\mu}_1(X_i))}{\hat{e}(X_i)}
- \frac{(1-A_i)(Y_i - \hat{\mu}_0(X_i))}{1 - \hat{e}(X_i)}
\]

where \(\hat{e}(X_i)\) is the online propensity model and \(\hat{\mu}_a(X_i)\) are online outcome models.

## Safety and evidence boundaries

This repository is intentionally transparent about what it does and does not prove:

- It includes **synthetic benchmarks** for method validation and optional **public CrUX/PageSpeed observational analysis** for real field-data ingestion.
- It does **not** fabricate Git history, deployment claims, user counts, company adoption, revenue impact, or real-world performance results.
- Public CrUX/PageSpeed observations should be labeled as public-origin field data, not private production telemetry.
- The code is suitable as a research artifact, prototype, or technical foundation for future empirical work.
- Any legal, immigration, grant, or publication submission should describe the repository accurately and attach real evidence only.

## Development commands

```bash
pytest -q
ruff check src tests
python benchmarks/run_synthetic.py --n-events 8000 --batch-size 400 --seed 11
```

## Citation

Please cite this repository using `CITATION.cff`.

## License

MIT License. See [`LICENSE`](LICENSE).
