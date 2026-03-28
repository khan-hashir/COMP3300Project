from __future__ import annotations

from typing import List

from task import Task


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
        avg_turnaround = round(sum(turnaround.values()) / n, 2)
        avg_waiting = round(sum(waiting.values()) / n, 2)

        return {
            "turnaround": turnaround,
            "waiting": waiting,
            "avg_turnaround": avg_turnaround,
            "avg_waiting": avg_waiting,
        }
