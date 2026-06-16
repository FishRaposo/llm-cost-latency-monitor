"""Smoke tests: the demo and integration examples run end-to-end offline."""

import subprocess
import sys
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def _run(script: str):
    result = subprocess.run(
        [sys.executable, str(EXAMPLES / script)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result


def test_demo_runs():
    result = _run("run_demo.py")
    assert result.returncode == 0, result.stderr
    assert "Demo complete." in result.stdout


def test_wrapped_fastapi_example_runs():
    result = _run("wrapped_fastapi_app.py")
    assert result.returncode == 0, result.stderr
    assert "smoke complete" in result.stdout


def test_wrapped_rag_example_runs():
    result = _run("wrapped_rag_app.py")
    assert result.returncode == 0, result.stderr
    assert "complete" in result.stdout
