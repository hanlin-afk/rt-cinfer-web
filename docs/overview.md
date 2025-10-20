# Energy-Efficient Task Allocation Strategies for Green Cloud Data Centers

This documentation-first repository describes a rigorous framework for **energy-aware, carbon-aware, and SLO-aware** scheduling in cloud data centers. It is intended as a **research companion** and can be extended into a codebase by implementing the interfaces documented in `docs/api.md`.

We articulate:
- A **power model** combining dynamic and static power for CPU/GPU/Memory/Network and cooling overhead (PUE).
- **Scheduling policies**: heuristics (DVFS-aware Greedy), optimization (MILP/ILP), and learning-based (RL).
- A **measurement protocol** and **reporting template** for energy/latency/carbon/fairness.

> Tip: Use this repo as the scaffolding for your paper and open-source artifacts. Keep all experiment parameters and seeds in the docs.
