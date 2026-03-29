import pytest

@pytest.mark.parametrize(
    ("payload", "expected_substring"),
    [
        (
            {"policy": "RR", "jobs": [{"pid": "A", "arrival": 0, "burst": 1, "priority": 1}]},
            "RR policy requires a quantum field",
        ),
        ({"policy": "FIFO", "jobs": []}, "jobs must not be empty"),
        (
            {
                "policy": "FIFO",
                "jobs": [
                    {"pid": "A", "arrival": 0, "burst": 1, "priority": 1},
                    {"pid": "A", "arrival": 1, "burst": 1, "priority": 1},
                ],
            },
            "Duplicate pid",
        ),
        (
            {
                "policy": "FIFO",
                "jobs": [
                    {"pid": "A", "arrival": True, "burst": 1, "priority": 1},
                ],
            },
            "jobs[0].arrival must be an integer (got boolean)",
        ),
        (
            {
                "policy": "FCFS",
                "jobs": [{"pid": "A", "arrival": 0, "burst": 1, "priority": 1}],
            },
            "Unsupported policy",
        ),
    ],
)
def test_invalid_inputs_exit_nonzero_and_emit_stderr(
    run_main_with_payload, payload: dict, expected_substring: str
):
    cp = run_main_with_payload(payload)
    assert cp.returncode == 1
    assert expected_substring in cp.stderr
    assert cp.stdout == ""


def test_idle_cpu_edge_case_fast_forwards_to_first_arrival(build_output_from_payload):
    raw = {
        "policy": "FIFO",
        "jobs": [{"pid": "LATE", "arrival": 5, "burst": 3, "priority": 1}],
    }
    out = build_output_from_payload(raw)
    assert out["gantt"] == [{"pid": "LATE", "start": 5, "end": 8}]
    assert out["metrics"]["turnaround"] == {"LATE": 3}
    assert out["metrics"]["waiting"] == {"LATE": 0}


def test_single_job_edge_case_has_zero_waiting(build_output_from_payload):
    raw = {
        "policy": "SJF",
        "jobs": [{"pid": "ONLY", "arrival": 0, "burst": 4, "priority": 2}],
    }
    out = build_output_from_payload(raw)
    assert out["gantt"] == [{"pid": "ONLY", "start": 0, "end": 4}]
    assert out["metrics"]["turnaround"] == {"ONLY": 4}
    assert out["metrics"]["waiting"] == {"ONLY": 0}
    assert out["metrics"]["avg_turnaround"] == 4.0
    assert out["metrics"]["avg_waiting"] == 0.0


def test_messy_key_normalization_matches_clean_input(build_output_from_payload):
    clean = {
        "policy": "RR",
        "quantum": 2,
        "jobs": [
            {"pid": "A", "arrival": 0, "burst": 6, "priority": 3},
            {"pid": "B", "arrival": 4, "burst": 4, "priority": 1},
            {"pid": "C", "arrival": 6, "burst": 3, "priority": 2},
        ],
    }
    messy = {
        " policy ": "  rr  ",
        " quantum ": 2,
        " jobs ": [
            {" pid ": " A ", " arrival ": 0, " burst ": 6, " priority ": 3},
            {" pid ": " B ", " arrival ": 4, " burst ": 4, " priority ": 1},
            {" pid ": " C ", " arrival ": 6, " burst ": 3, " priority ": 2},
        ],
    }
    clean_out = build_output_from_payload(clean)
    messy_out = build_output_from_payload(messy)

    assert messy_out == clean_out
