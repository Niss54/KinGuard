"""Run actual browser lifecycle functions with controlled SDK/network responses."""
import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.parametrize("suite", ["hybrid", "dashboard"])
def test_browser_runtime(suite):
    node = shutil.which("node")
    assert node, "Install Node.js to run browser regression tests"
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [node, "--test", f"tests/js/{suite}.test.cjs"], cwd=root,
        capture_output=True, text=True, encoding="utf-8", timeout=30, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
