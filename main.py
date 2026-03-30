import json
import sys

from input_normalize import normalize_input
from input_validate import validate_input
from metrics import ScheduleMetrics
from scheduler import Scheduler, gantt_to_dicts
from task import Task


def format_schedule_json(data: dict) -> str:
    lines = ["{"]
    lines.append(f'  "policy": {json.dumps(data["policy"], allow_nan=False)},')
    lines.append('  "gantt": [')
    gantt = data["gantt"]
    for i, seg in enumerate(gantt):
        tail = "," if i < len(gantt) - 1 else ""
        lines.append(f"    {json.dumps(seg, allow_nan=False)}{tail}")
    lines.append("  ],")
    m = data["metrics"]
    lines.append('  "metrics": {')
    lines.append(f'    "turnaround": {json.dumps(m["turnaround"], allow_nan=False)},')
    lines.append(f'    "waiting": {json.dumps(m["waiting"], allow_nan=False)},')
    lines.append(f'    "avg_turnaround": {json.dumps(m["avg_turnaround"], allow_nan=False)},')
    lines.append(f'    "avg_waiting": {json.dumps(m["avg_waiting"], allow_nan=False)}')
    lines.append("  }")
    lines.append("}")
    return "\n".join(lines) + "\n"


def parse_tasks(json_load) -> Scheduler:
    jobs = json_load["jobs"]
    parsed_jobs = [
        Task(j["pid"], j["arrival"], j["burst"], j["priority"]) for j in jobs
    ]
    quantum = json_load.get("quantum", 0)
    policy = str(json_load["policy"]).strip().upper()
    return Scheduler(policy, parsed_jobs, quantum)


def build_output(scheduler: Scheduler, gantt) -> dict:
    policy = scheduler.policy.strip().upper()
    metrics = ScheduleMetrics(scheduler.jobs).to_dict()
    return {
        "policy": policy,
        "gantt": gantt_to_dicts(gantt),
        "metrics": metrics,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <input.json>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file) as f:
        json_load = normalize_input(json.load(f))
    try:
        validate_input(json_load)
    except ValueError as err:
        print(err, file=sys.stderr)
        sys.exit(1)

    scheduler = parse_tasks(json_load)
    gantt = scheduler.schedule()
    out = build_output(scheduler, gantt)

    print(format_schedule_json(out))
