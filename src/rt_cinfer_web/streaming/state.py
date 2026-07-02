"""Pipeline state containers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StreamState:
    n_events: int = 0
    n_batches: int = 0
    active_drift_flags: dict[str, bool] = field(default_factory=dict)
    last_metrics: dict[str, float] = field(default_factory=dict)

    def update_counts(self, batch_size: int) -> None:
        self.n_events += int(batch_size)
        self.n_batches += 1
