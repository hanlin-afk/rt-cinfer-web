# Energy & Power Model

Let `P_total = P_it + P_cooling`, where `P_cooling = (PUE - 1) * P_it` and `P_it` is the IT load power.
For CPU, `P_cpu = P_static + C * f * V^2` where DVFS couples `f` and `V`. For GPUs, include SM/Memory rails.

**Task Energy**: `E_task = ∫ P_total(t) dt` during task execution.

**Thermal constraints**: model temperature via RC network or empirical linear model vs. utilization to penalize hot placement.
