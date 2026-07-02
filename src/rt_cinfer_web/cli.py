"""Command-line interface for RT-CInfer-Web."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rt_cinfer_web.data.synthetic import SyntheticWebVitalsStream
from rt_cinfer_web.pipeline import PipelineConfig, RealTimeCausalPipeline


def _cmd_benchmark(args: argparse.Namespace) -> int:
    stream = SyntheticWebVitalsStream(seed=args.seed, drift_at=args.drift_at)
    pipeline = RealTimeCausalPipeline(PipelineConfig(metric=args.metric, treatment=args.treatment))
    report = None
    for batch in stream.iter_batches(n_events=args.n_events, batch_size=args.batch_size):
        report = pipeline.update(batch)
    if report is None:
        raise RuntimeError("No report generated")
    output = report.as_dict()
    text = json.dumps(output, indent=2, default=str)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text, encoding="utf-8")
    print(text)
    return 0


def _cmd_generate(args: argparse.Namespace) -> int:
    df = SyntheticWebVitalsStream(seed=args.seed, drift_at=args.drift_at).generate(args.n_events)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Wrote {len(df)} events to {args.output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RT-CInfer-Web CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    bench = sub.add_parser("benchmark", help="Run a synthetic streaming benchmark")
    bench.add_argument("--n-events", type=int, default=5000)
    bench.add_argument("--batch-size", type=int, default=250)
    bench.add_argument("--seed", type=int, default=7)
    bench.add_argument("--drift-at", type=int, default=2500)
    bench.add_argument("--metric", default="lcp_ms")
    bench.add_argument("--treatment", default="edge_cache_enabled")
    bench.add_argument("--output", default=None)
    bench.set_defaults(func=_cmd_benchmark)

    gen = sub.add_parser("generate", help="Generate synthetic web-vitals events")
    gen.add_argument("--n-events", type=int, default=1000)
    gen.add_argument("--seed", type=int, default=7)
    gen.add_argument("--drift-at", type=int, default=500)
    gen.add_argument("--output", default="data/samples/synthetic_web_vitals.csv")
    gen.set_defaults(func=_cmd_generate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
