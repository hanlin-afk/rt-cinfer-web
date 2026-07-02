from __future__ import annotations

import argparse
from pathlib import Path

from rt_cinfer_web.data.synthetic import SyntheticWebVitalsStream


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-events", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--output", default="data/samples/synthetic_web_vitals.csv")
    args = parser.parse_args()
    df = SyntheticWebVitalsStream(seed=args.seed).generate(args.n_events)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Wrote {len(df)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
