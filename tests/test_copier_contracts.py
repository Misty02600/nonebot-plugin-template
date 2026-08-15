from __future__ import annotations

import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
STABLE_ANSWER_KEYS = {
    "author_email",
    "author_name",
    "copyright_year",
    "module_name",
    "repo_name",
    "repo_owner",
}


def test_copier_keeps_the_nonebot_answer_schema() -> None:
    configuration = (REPOSITORY_ROOT / "copier.yml").read_text(encoding="utf-8")
    question_keys = set(
        re.findall(r"^([a-z][a-z0-9_]*):\n", configuration, flags=re.MULTILINE)
    )

    assert STABLE_ANSWER_KEYS <= question_keys
    assert "project_description" not in question_keys
    assert "_subdirectory: template" in configuration
    assert "tasks:" not in configuration
    assert "migrations:" not in configuration


def test_copier_and_controller_use_the_same_supported_major_line() -> None:
    configuration = (REPOSITORY_ROOT / "copier.yml").read_text(encoding="utf-8")
    justfile = (REPOSITORY_ROOT / "justfile").read_text(encoding="utf-8")

    assert '_min_copier_version: "9.17.0"' in configuration
    assert "copier>=9.17,<10" in justfile
