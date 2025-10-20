# Algorithms

## 1) DVFS-Aware Greedy (Heuristic)
- Sort tasks by priority (deadline, slack).
- For each task, choose node+DVFS pair minimizing `α*Energy + β*Latency + γ*SLO_violation_prob`.

## 2) MILP/ILP Baseline
- Variables: x_{t,n} ∈ {0,1} (task t on node n), y_n ∈ {0,1} (node on/off), s_n DVFS state.
- Objective: minimize `Energy + λ*Penalty_SLO + μ*Penalty_Fairness` subject to capacity, affinity, and deadline constraints.

## 3) RL Agent (e.g., PPO)
- State: queue features, node utilizations, temp, DVFS states, predicted CI.
- Action: assign task to node + choose DVFS state; optional consolidation action at epoch boundaries.
- Reward: negative of multi-objective cost; include shaping for SLO and thermal margins.

## 4) Consolidation & Sleep
- Periodically pack workloads to power down idle nodes, respecting wake penalties and queueing delay.
