import json
import subprocess
import sys
from pathlib import Path

import pytest

from input_normalize import normalize_input
from input_validate import validate_input
from main import build_output, parse_tasks


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def main_py(project_root: Path) -> Path:
    return project_root / "main.py"


@pytest.fixture(scope="session")
def fixtures_dir(project_root: Path) -> Path:
    return project_root / "tests" / "fixtures"


@pytest.fixture(scope="session")
def load_fixture_json(fixtures_dir: Path):
    def _load(name: str) -> dict:
        return json.loads((fixtures_dir / name).read_text(encoding="utf-8"))

    return _load


@pytest.fixture()
def run_main_cli(main_py: Path):
    def _run(input_path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(main_py), str(input_path)],
            capture_output=True,
            text=True,
            check=False,
        )

    return _run


@pytest.fixture()
def run_main_with_payload(tmp_path: Path, run_main_cli):
    def _run(payload: dict) -> subprocess.CompletedProcess[str]:
        path = tmp_path / "input.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return run_main_cli(path)

    return _run


@pytest.fixture()
def build_output_from_payload():
    def _build(raw_payload: dict) -> dict:
        data = normalize_input(raw_payload)
        validate_input(data)
        scheduler = parse_tasks(data)
        return build_output(scheduler, scheduler.schedule())

    return _build
