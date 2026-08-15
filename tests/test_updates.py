from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def run(*arguments: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        arguments,
        cwd=cwd,
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, (
        f"command failed ({result.returncode}): {' '.join(arguments)}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    return result


def configure_git(repository: Path) -> None:
    run("git", "init", "-b", "main", cwd=repository)
    run("git", "config", "user.name", "Template Test", cwd=repository)
    run("git", "config", "user.email", "template@example.invalid", cwd=repository)
    run("git", "config", "commit.gpgsign", "false", cwd=repository)
    run("git", "config", "tag.gpgSign", "false", cwd=repository)


def commit_and_tag(repository: Path, version: str) -> None:
    run("git", "add", ".", cwd=repository)
    run("git", "commit", "-m", f"template {version}", cwd=repository)
    run("git", "tag", "-a", version, "-m", version, cwd=repository)


def test_generated_project_survives_a_real_copier_update(
    template_snapshot: Path,
    tmp_path: Path,
) -> None:
    source = template_snapshot
    configure_git(source)
    commit_and_tag(source, "v0.1.0")

    destination = tmp_path / "generated-project"
    run(
        sys.executable,
        "-m",
        "copier",
        "copy",
        "--defaults",
        "--data",
        "repo_owner=TemplateTest",
        "--data",
        "repo_name=nonebot-plugin-example",
        "--data",
        "module_name=nonebot_plugin_example",
        f"git+{source.as_uri()}",
        str(destination),
        cwd=tmp_path,
    )
    answers = (destination / ".copier-answers.yml").read_text(encoding="utf-8")
    assert "_commit: v0.1.0" in answers

    configure_git(destination)
    run("git", "add", ".", cwd=destination)
    run("git", "commit", "-m", "generate from template v0.1.0", cwd=destination)
    readme = destination / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + "\nConsumer-owned note.\n",
        encoding="utf-8",
    )
    run("git", "add", "README.md", cwd=destination)
    run("git", "commit", "-m", "add consumer note", cwd=destination)

    readme_template = source / "template/README.md.jinja"
    readme_template.write_text(
        "<!-- template v0.2.0 -->\n" + readme_template.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (source / "template/template-added.txt").write_text(
        "added by template v0.2.0\n",
        encoding="utf-8",
    )
    commit_and_tag(source, "v0.2.0")

    run(
        sys.executable,
        "-m",
        "copier",
        "update",
        "--skip-answered",
        str(destination),
        cwd=tmp_path,
    )

    updated_readme = readme.read_text(encoding="utf-8")
    assert "<!-- template v0.2.0 -->" in updated_readme
    assert "Consumer-owned note." in updated_readme
    assert "<<<<<<<" not in updated_readme
    assert (destination / "template-added.txt").read_text(encoding="utf-8") == (
        "added by template v0.2.0\n"
    )
    answers = (destination / ".copier-answers.yml").read_text(encoding="utf-8")
    assert "_commit: v0.2.0" in answers
    run("git", "diff", "--check", cwd=destination)
    assert not list(destination.rglob("*.rej"))
