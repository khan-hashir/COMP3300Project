import json
import sys

from scheduler import Scheduler, gantt_to_dicts
from task import Task


def parse_tasks(json_load) -> Scheduler:
    jobs = json_load["jobs"]
    parsed_jobs = [
        Task(j["pid"], j["arrival"], j["burst"], j["priority"]) for j in jobs
    ]
    quantum = json_load.get("quantum", 0)
    policy = str(json_load["policy"]).strip().upper()
    return Scheduler(policy, parsed_jobs, quantum)



def build_output(scheduler: Scheduler, gantt) -> dict:
    """Top-level result for JSON stdout (Phase 1.2: policy + gantt)."""
    policy = scheduler.policy.strip().upper()
    return {
        "policy": policy,
        "gantt": gantt_to_dicts(gantt),
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <input.json>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file) as f:
        json_load = json.load(f)

    scheduler = parse_tasks(json_load)
    gantt = scheduler.schedule()
    out = build_output(scheduler, gantt)

    print(json.dumps(out))
