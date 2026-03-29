import json
from pathlib import Path

import pytest

from input_normalize import normalize_input
from input_validate import validate_input
from main import build_output, parse_tasks

_FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"

_EXPECTED_PRIORITY = {
    "policy": "PRIORITY",
    "gantt": [
        {"pid": "B", "start": 0, "end": 2},
        {"pid": "C", "start": 2, "end": 5},
        {"pid": "A", "start": 5, "end": 9},
        {"pid": "D", "start": 9, "end": 10},
    ],
    "metrics": {
        "turnaround": {"A": 9, "B": 2, "C": 4, "D": 8},
        "waiting": {"A": 5, "B": 0, "C": 1, "D": 7},
        "avg_turnaround": 5.75,
        "avg_waiting": 3.25,
    },
}


def test_priority_golden_matches_fixture_file():
    path = _FIXTURE_DIR / "priority.json"
    assert path.is_file(), f"missing fixture: {path}"
    raw = json.loads(path.read_text(encoding="utf-8"))
    data = normalize_input(raw)
    validate_input(data)
    scheduler = parse_tasks(data)
    out = build_output(scheduler, scheduler.schedule())
    assert out == _EXPECTED_PRIORITY


def test_priority_equal_priority_uses_lexicographic_pid_tiebreak():
    raw = {
        "policy": "PRIORITY",
        "jobs": [
            {"pid": "B", "arrival": 0, "burst": 2, "priority": 1},
            {"pid": "A", "arrival": 0, "burst": 2, "priority": 1},
            {"pid": "C", "arrival": 0, "burst": 2, "priority": 2},
        ],
    }
    data = normalize_input(raw)
    validate_input(data)
    scheduler = parse_tasks(data)
    out = build_output(scheduler, scheduler.schedule())
    assert [x["pid"] for x in out["gantt"]] == ["A", "B", "C"]


@pytest.mark.parametrize("policy_spacing", ["PRIORITY", "  priority  "])
def test_priority_policy_normalization(policy_spacing: str):
    raw = {
        "policy": policy_spacing,
        "jobs": [
            {"pid": "A", "arrival": 0, "burst": 4, "priority": 2},
            {"pid": "B", "arrival": 0, "burst": 2, "priority": 1},
            {"pid": "C", "arrival": 1, "burst": 3, "priority": 1},
            {"pid": "D", "arrival": 2, "burst": 1, "priority": 3},
        ],
    }
    data = normalize_input(raw)
    validate_input(data)
    scheduler = parse_tasks(data)
    out = build_output(scheduler, scheduler.schedule())
    assert out == _EXPECTED_PRIORITY
