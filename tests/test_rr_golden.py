import json
from pathlib import Path

import pytest

from input_normalize import normalize_input
from input_validate import validate_input
from main import build_output, parse_tasks

_FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"

_EXPECTED_RR = {
    "policy": "RR",
    "gantt": [
        {"pid": "A", "start": 0, "end": 2},
        {"pid": "A", "start": 2, "end": 4},
        {"pid": "A", "start": 4, "end": 6},
        {"pid": "B", "start": 6, "end": 8},
        {"pid": "C", "start": 8, "end": 10},
        {"pid": "B", "start": 10, "end": 12},
        {"pid": "C", "start": 12, "end": 13},
    ],
    "metrics": {
        "turnaround": {"A": 6, "B": 8, "C": 7},
        "waiting": {"A": 0, "B": 4, "C": 4},
        "avg_turnaround": 7.0,
        "avg_waiting": 2.67,
    },
}


def test_rr_golden_matches_fixture_file():
    path = _FIXTURE_DIR / "rr.json"
    assert path.is_file(), f"missing fixture: {path}"
    raw = json.loads(path.read_text(encoding="utf-8"))
    data = normalize_input(raw)
    validate_input(data)
    scheduler = parse_tasks(data)
    out = build_output(scheduler, scheduler.schedule())
    assert out == _EXPECTED_RR


def test_rr_quantum_slicing_keeps_segments_within_quantum():
    raw = {
        "policy": "RR",
        "quantum": 2,
        "jobs": [
            {"pid": "A", "arrival": 0, "burst": 5, "priority": 1},
            {"pid": "B", "arrival": 0, "burst": 3, "priority": 1},
        ],
    }
    data = normalize_input(raw)
    validate_input(data)
    scheduler = parse_tasks(data)
    out = build_output(scheduler, scheduler.schedule())
    for seg in out["gantt"]:
        assert 1 <= (seg["end"] - seg["start"]) <= 2


def test_rr_equal_arrival_uses_lexicographic_pid_tiebreak():
    """Equal arrival: ready queue follows PID order; B before A in JSON disproves list-order scheduling."""
    raw = {
        "policy": "RR",
        "quantum": 2,
        "jobs": [
            {"pid": "B", "arrival": 0, "burst": 4, "priority": 1},
            {"pid": "A", "arrival": 0, "burst": 4, "priority": 1},
        ],
    }
    data = normalize_input(raw)
    validate_input(data)
    scheduler = parse_tasks(data)
    out = build_output(scheduler, scheduler.schedule())
    assert out["gantt"] == [
        {"pid": "A", "start": 0, "end": 2},
        {"pid": "B", "start": 2, "end": 4},
        {"pid": "A", "start": 4, "end": 6},
        {"pid": "B", "start": 6, "end": 8},
    ]
    assert out["metrics"]["turnaround"] == {"A": 6, "B": 8}
    assert out["metrics"]["waiting"] == {"A": 2, "B": 4}
    assert out["metrics"]["avg_turnaround"] == 7.0
    assert out["metrics"]["avg_waiting"] == 3.0


@pytest.mark.parametrize("policy_spacing", ["RR", "  rr  "])
def test_rr_policy_normalization(policy_spacing: str):
    raw = {
        "policy": policy_spacing,
        "quantum": 2,
        "jobs": [
            {"pid": "A", "arrival": 0, "burst": 6, "priority": 3},
            {"pid": "B", "arrival": 4, "burst": 4, "priority": 1},
            {"pid": "C", "arrival": 6, "burst": 3, "priority": 2},
        ],
    }
    data = normalize_input(raw)
    validate_input(data)
    scheduler = parse_tasks(data)
    out = build_output(scheduler, scheduler.schedule())
    assert out == _EXPECTED_RR
