# Experiments

## Metrics
- **Energy** (Wh/task, Wh/throughput), **Carbon** (gCO₂e/task), **Latency** (p95/p99), **SLO miss %**, **Fairness** (Jain index), **Utilization**, **Thermal headroom**.

## Baselines
- Random, First‑Fit, DVFS‑Greedy, MILP/ILP, RL (PPO).

## Protocol
1. Fix random seeds, simulator version, and dataset slice.
2. Run each method over N seeds (≥5) and report mean ± 95% CI.
3. Use paired tests (e.g., Wilcoxon) for significance when appropriate.

## Ablations
- Remove carbon oracle, vary PUE, disable DVFS, change CI profiles, enable thermal penalties.

## Reporting
Use `docs/results-template.md` to log tables and figures with exact commands.
