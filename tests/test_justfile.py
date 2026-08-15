from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_root_justfile_exposes_the_controller_quality_commands() -> None:
    justfile = (REPOSITORY_ROOT / "justfile").read_text(encoding="utf-8")

    assert 'set minimum-version := "1.56.0"' in justfile
    assert '[windows]\nset shell := ["pwsh", "-NoProfile", "-Command"]' in justfile
    for recipe in ("test", "test-fast", "lint", "format", "check", "lock"):
        assert f"\n{recipe}:\n" in justfile

    assert 'uv run pytest -m "not integration"' in justfile
    assert "uv run ruff check .\n" in justfile
    assert "uv run ruff format --check ." in justfile
    assert "uv run basedpyright" in justfile
    assert "uv lock" in justfile
    assert (
        '[confirm("确认在 main 上创建模板版本提交和 annotated tag，'
        '并整体原子推送到 origin？")]' in justfile
    )
    assert 'shell("git branch --show-current") == "main"' in justfile
    assert 'error("bump 只能在 main 分支执行")' in justfile
    assert "git push --atomic --follow-tags origin HEAD" in justfile
    assert "cz version --project --tag" not in justfile


def test_creation_recipe_does_not_collect_a_project_description() -> None:
    justfile = (REPOSITORY_ROOT / "justfile").read_text(encoding="utf-8")

    assert 'new name visibility="public":' in justfile
    assert "project_description" not in justfile
    assert "--description" not in justfile
    assert 'commit -m "chore: initialize repository"' in justfile


def test_generated_run_recipe_uses_the_synced_nonebot_cli() -> None:
    justfile = (REPOSITORY_ROOT / "template/justfile").read_text(encoding="utf-8")

    assert "uv sync --all-groups" in justfile
    assert "uv run nb run --reload" in justfile


def test_generated_justfile_has_resumable_template_updates() -> None:
    justfile = (REPOSITORY_ROOT / "template/justfile").read_text(encoding="utf-8")
    update_start = justfile.index("update-template:")
    finish_start = justfile.index("finish-template-update:")
    hooks_start = justfile.index("# 安装 pre-commit")
    update_recipe = justfile[update_start:finish_start]
    finish_recipe = justfile[finish_start:hooks_start]

    assert "set lazy" in justfile
    assert 'shell("git status --porcelain --untracked-files=normal")' in justfile
    assert "copier update --skip-answered" in update_recipe
    assert "--vcs-ref" not in update_recipe
    assert "just finish-template-update" in update_recipe

    ordered_commands = (
        "git diff --check",
        "git diff --cached --check",
        "'*.rej'",
        "uv lock",
        "uv sync --locked --all-groups",
        "uv run --no-sync prek run --all-files",
        "uv run --no-sync ruff check .",
        "uv run --no-sync ruff format --check .",
        "uv run --no-sync basedpyright",
        "uv run --no-sync pytest",
    )
    positions = [finish_recipe.index(command) for command in ordered_commands]
    assert positions == sorted(positions)

    assert "uv run prek update --cooldown-days 7" in justfile
    assert "prek auto-update" not in justfile
    assert "uv run ruff check .\n" in justfile
    assert "uv run ruff format --check ." in justfile


def test_generated_bump_pushes_the_whole_release_from_main() -> None:
    justfile = (REPOSITORY_ROOT / "template/justfile").read_text(encoding="utf-8")
    bump_start = justfile.index("bump:")
    changelog_start = justfile.index("# 生成 changelog")
    bump_recipe = justfile[bump_start:changelog_start]

    assert (
        '[confirm("确认在 main 上创建版本提交和 annotated tag，并整体原子推送到 origin？")]'
        in justfile
    )
    assert 'shell("git branch --show-current") == "main"' in bump_recipe
    assert 'error("bump 只能在 main 分支执行")' in bump_recipe
    assert "uv run cz bump --yes" in bump_recipe
    assert "uv lock" in bump_recipe
    assert "git push --atomic --follow-tags origin HEAD" in bump_recipe
    assert "cz version" not in bump_recipe
    assert "push-release:" not in justfile


@dataclass(frozen=True)
class NewRecipeHarness:
    template: Path
    environment: dict[str, str]
    call_log: Path

    def invoke(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ("just", "--justfile", str(self.template / "justfile"), *arguments),
            cwd=self.template,
            env=self.environment,
            check=False,
            text=True,
            encoding="utf-8",
            capture_output=True,
        )

    def read_calls(self) -> list[dict[str, Any]]:
        if not self.call_log.exists():
            return []
        return [
            json.loads(line)
            for line in self.call_log.read_text(encoding="utf-8").splitlines()
        ]


@pytest.fixture
def new_recipe_harness(tmp_path: Path) -> NewRecipeHarness:
    if shutil.which("pwsh") is None or shutil.which("just") is None:
        pytest.skip("pwsh and just are required")

    template = tmp_path / "template"
    template.mkdir()
    shutil.copy2(REPOSITORY_ROOT / "justfile", template / "justfile")

    bin_directory = tmp_path / "bin"
    bin_directory.mkdir()
    call_log = tmp_path / "calls.jsonl"
    capture_script = tmp_path / "capture.py"
    capture_script.write_text(
        """from __future__ import annotations

import json
import os
import sys
from pathlib import Path

tool, *arguments = sys.argv[1:]
target = (Path(os.environ["STUB_TEMPLATE_ROOT"]).parent / os.environ["name"]).resolve()
with Path(os.environ["CALL_LOG"]).open("a", encoding="utf-8") as file:
    file.write(json.dumps({"tool": tool, "arguments": arguments}) + "\\n")
if tool == "git" and arguments[-2:] == ["rev-parse", "--show-toplevel"]:
    print(os.environ["STUB_TEMPLATE_ROOT"])
elif tool == "git" and arguments[-3:] == ["remote", "get-url", "origin"]:
    print("git@github.com:TemplateFork/nonebot-plugin-template.git")
elif tool == "git" and arguments[:1] == ["ls-remote"]:
    print("0" * 40 + "\\tHEAD")
elif tool == "gh" and arguments == ["api", "user", "--jq", ".login"]:
    print("Authenticated-Owner")
elif tool == "uvx":
    target.mkdir()
""",
        encoding="utf-8",
    )
    python = str(Path(sys.executable)).replace("'", "''")
    capture = str(capture_script).replace("'", "''")
    for tool in ("uvx", "git", "gh"):
        (bin_directory / f"{tool}.ps1").write_text(
            f"& '{python}' '{capture}' '{tool}' @args\nexit $LASTEXITCODE\n",
            encoding="utf-8",
        )

    environment = os.environ.copy()
    environment["PATH"] = f"{bin_directory}{os.pathsep}{environment['PATH']}"
    if sys.platform == "win32":
        environment["PATHEXT"] = f".PS1;{environment.get('PATHEXT', '')}"
    environment["CALL_LOG"] = str(call_log)
    environment["STUB_TEMPLATE_ROOT"] = str(template.resolve())
    return NewRecipeHarness(template, environment, call_log)


@pytest.mark.integration
def test_new_recipe_orchestrates_creation_without_a_description(
    new_recipe_harness: NewRecipeHarness,
) -> None:
    result = new_recipe_harness.invoke("new", "nonebot-plugin-stub", "private")
    assert result.returncode == 0, result.stderr

    calls = new_recipe_harness.read_calls()
    assert [call["tool"] for call in calls] == [
        "git",
        "git",
        "git",
        "gh",
        "uvx",
        "git",
        "git",
        "git",
        "gh",
    ]
    copier_arguments = calls[4]["arguments"]
    assert copier_arguments[-2:] == [
        "https://github.com/TemplateFork/nonebot-plugin-template.git",
        str(new_recipe_harness.template.parent / "nonebot-plugin-stub"),
    ]
    assert "repo_owner=Authenticated-Owner" in copier_arguments
    assert "repo_name=nonebot-plugin-stub" in copier_arguments
    assert not any("description" in argument for argument in copier_arguments)
    assert calls[7]["arguments"][-2:] == [
        "-m",
        "chore: initialize repository",
    ]
    assert calls[8]["arguments"][:3] == [
        "repo",
        "create",
        "Authenticated-Owner/nonebot-plugin-stub",
    ]
    assert "--description" not in calls[8]["arguments"]
