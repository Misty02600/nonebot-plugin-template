from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def template_snapshot(tmp_path: Path) -> Path:
    snapshot = tmp_path / "template-source"
    shutil.copytree(
        REPOSITORY_ROOT,
        snapshot,
        ignore=shutil.ignore_patterns(
            ".git",
            ".venv",
            ".pytest_cache",
            ".ruff_cache",
            ".basedpyright",
            "__pycache__",
            "_generated",
            "uv.lock",
        ),
    )
    return snapshot
