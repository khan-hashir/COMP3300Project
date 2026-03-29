import json

import pytest

_EXPECTED_BY_FIXTURE = {
    "fifo.json": {
        "policy": "FIFO",
        "gantt": [
            {"pid": "A", "start": 0, "end": 4},
            {"pid": "B", "start": 4, "end": 6},
        ],
        "metrics": {
            "turnaround": {"A": 4, "B": 4},
            "waiting": {"A": 0, "B": 2},
            "avg_turnaround": 4.0,
            "avg_waiting": 1.0,
        },
    },
    "sjf.json": {
        "policy": "SJF",
        "gantt": [
            {"pid": "B", "start": 0, "end": 2},
            {"pid": "D", "start": 2, "end": 3},
            {"pid": "C", "start": 3, "end": 5},
            {"pid": "A", "start": 5, "end": 10},
        ],
        "metrics": {
            "turnaround": {"A": 10, "B": 2, "C": 4, "D": 1},
            "waiting": {"A": 5, "B": 0, "C": 2, "D": 0},
            "avg_turnaround": 4.25,
            "avg_waiting": 1.75,
        },
    },
    "priority.json": {
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
    },
    "rr.json": {
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
    },
}


@pytest.mark.parametrize("fixture_name", ["fifo.json", "sjf.json", "priority.json", "rr.json"])
def test_main_cli_outputs_expected_json_for_fixtures(
    fixture_name: str, fixtures_dir, run_main_cli
):
    fixture_path = fixtures_dir / fixture_name
    completed = run_main_cli(fixture_path)
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    actual = json.loads(completed.stdout)
    assert actual == _EXPECTED_BY_FIXTURE[fixture_name]
