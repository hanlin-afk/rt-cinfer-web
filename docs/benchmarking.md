# Benchmarking Guide

## Synthetic benchmark

Run:

```bash
python benchmarks/run_synthetic.py --n-events 8000 --batch-size 400 --seed 11
```

The benchmark reports:

- final online doubly robust ATE estimate;
- confidence interval;
- treatment share and overlap rate;
- recent Web Vitals summary;
- drift flags;
- bottleneck localization;
- recommendation decision.

## Interpreting signs

For latency metrics, negative ATE means the intervention reduces the metric and is therefore beneficial.

## Known ground truth

The synthetic generator uses these default effects:

- edge cache effect on LCP: -120 ms
- image optimization effect on LCP: -85 ms
- JavaScript deferral effect on FID: -18 ms
- layout reserve effect on CLS: -0.035

The online estimator will not exactly equal ground truth because the data is noisy, treatment assignment is confounded, and the estimator learns nuisance models online.
