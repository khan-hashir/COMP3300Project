from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import List

from task import Task


_AVG_QUANT = Decimal("0.01")

def _mean_two_decimals(total: int, count: int) -> float:
    if count <= 0:
        raise ValueError("count must be positive")
    q = (Decimal(total) / Decimal(count)).quantize(
        _AVG_QUANT, rounding=ROUND_HALF_UP
    )
    return float(q)


class ScheduleMetrics:

    def __init__(self, jobs: List[Task]) -> None:
        if not jobs:
            raise ValueError("Cannot compute metrics for an empty job list")
        for task in jobs:
            if task.finish_time is None:
                raise ValueError(
                    f"Task {task.pid!r} has no finish_time; run the scheduler first"
                )
        self._jobs = jobs

    def to_dict(self) -> dict:
        ordered = sorted(self._jobs, key=lambda t: t.pid)
        turnaround: dict[str, int] = {}
        waiting: dict[str, int] = {}
        for task in ordered:
            turnaround[task.pid] = task.turnaround_time()
            waiting[task.pid] = task.waiting_time()

        n = len(ordered)
        avg_turnaround = _mean_two_decimals(sum(turnaround.values()), n)
        avg_waiting = _mean_two_decimals(sum(waiting.values()), n)

        return {
            "turnaround": turnaround,
            "waiting": waiting,
            "avg_turnaround": avg_turnaround,
            "avg_waiting": avg_waiting,
        }
