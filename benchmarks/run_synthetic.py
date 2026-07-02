from __future__ import annotations

import argparse
import json
from pathlib import Path

from rt_cinfer_web.data.synthetic import SyntheticWebVitalsStream
from rt_cinfer_web.pipeline import PipelineConfig, RealTimeCausalPipeline


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-events", type=int, default=8000)
    parser.add_argument("--batch-size", type=int, default=400)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--drift-at", type=int, default=4000)
    parser.add_argument("--output", default="outputs/synthetic_benchmark_report.json")
    args = parser.parse_args()

    stream = SyntheticWebVitalsStream(seed=args.seed, drift_at=args.drift_at)
    pipeline = RealTimeCausalPipeline(PipelineConfig(metric="lcp_ms", treatment="edge_cache_enabled"))
    report = None
    for batch in stream.iter_batches(n_events=args.n_events, batch_size=args.batch_size):
        report = pipeline.update(batch)
    if report is None:
        raise RuntimeError("No data processed")

    output = report.as_dict()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    print(json.dumps(output["estimate"], indent=2, default=str))
    print(f"Wrote full report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
