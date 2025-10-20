# System Architecture

**Control Loop**: Observe cluster state → Predict load/energy/carbon → Decide allocation → Actuate (place tasks, set DVFS) → Measure → Learn.

**Major Components**
1. **Workload Ingress**: Trace replayer or synthetic generator (Poisson/Bursty).
2. **State Store**: Node metrics (util, temp), energy model params, carbon intensity feed.
3. **Schedulers**:
   - Heuristic: Greedy with DVFS and consolidation.
   - Optimization: ILP/MILP for batch windows.
   - RL Agent: Policy over placement and DVFS actions.
4. **Actuator**: Placement API + DVFS controller + cooldown constraints.
5. **Telemetry**: Collect energy (Wh), SLO miss rate, carbon (gCO₂e), thermal margins, fairness.

**Data Flow**
```
[Ingress] -> [State Store] -> [Scheduler] -> [Actuator] -> [Telemetry]
                   ^                                  |
                   +----------------------------------+
```
