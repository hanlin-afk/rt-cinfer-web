# API Contracts (to implement under `src/` later)

```python
class PowerModel(Protocol):
    def power(self, node_state: "NodeState", dvfs: float) -> float: ...
    def energy(self, trace: "ExecutionTrace") -> float: ...

class Scheduler(Protocol):
    def plan(self, pending_tasks: list["Task"], cluster: "ClusterState") -> "Decision":
        """Return placements and optional DVFS settings."""

class CarbonOracle(Protocol):
    def intensity(self, region: str, ts: float) -> float: ...  # gCO2e/kWh

class Simulator(Protocol):
    def step(self, decision: "Decision") -> "Observation": ...

# Data structures
@dataclass
class Task:
    id: str
    cpu: float; mem: float; gpu: float | None
    deadline_ms: int | None
    duration_ms: int
    priority: int = 0

@dataclass
class Node:
    id: str; region: str
    cpu_capacity: float; mem_capacity: float; gpu_capacity: float | None
    p_static: float; p_dyn_coeff: float; pue: float

@dataclass
class Decision:
    placements: list[tuple[str, str]]  # (task_id, node_id)
    dvfs: dict[str, float]             # node_id -> freq scalar [0,1]
```
