from __future__ import annotations

import json
import tomllib
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_controller_repository_has_a_reproducible_uv_environment() -> None:
    with (REPOSITORY_ROOT / "pyproject.toml").open("rb") as file:
        configuration = tomllib.load(file)

    assert configuration["project"]["license"] == "MIT"
    assert configuration["project"]["license-files"] == ["LICENSE"]
    license_text = (REPOSITORY_ROOT / "LICENSE").read_text(encoding="utf-8")
    assert license_text.startswith("MIT License\n\n")
    assert "nonebot-plugin-template contributors" in license_text
    assert configuration["tool"]["uv"]["package"] is False
    assert "required-version" not in configuration["tool"]["uv"]
    assert (REPOSITORY_ROOT / "uv.lock").is_file()
    ignored = set(
        (REPOSITORY_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    )
    assert "uv.lock" not in ignored


def test_controller_ci_checks_both_controller_and_generated_project() -> None:
    workflow = (REPOSITORY_ROOT / ".github/workflows/ci.yml").read_text(
        encoding="utf-8"
    )
    controller_job = workflow[
        workflow.index("  controller:") : workflow.index("  ruff:")
    ]
    ruff_job = workflow[workflow.index("  ruff:") : workflow.index("  basedpyright:")]
    basedpyright_job = workflow[
        workflow.index("  basedpyright:") : workflow.index("  test:")
    ]
    test_job = workflow[workflow.index("  test:") :]

    assert "uv sync --all-groups --locked" in controller_job
    assert "uv run --no-sync ruff check" in controller_job
    assert "uv run --no-sync basedpyright" in controller_job
    assert "uv run --no-sync pytest" in controller_job
    assert "uv sync --only-group lint" in ruff_job
    assert "uv run --no-sync ruff check" in ruff_job
    assert "uv sync --no-dev --group type" in basedpyright_job
    assert "uv run --no-sync basedpyright" in basedpyright_job
    assert "uv sync --no-dev --group test" in test_job
    assert "uv run --no-sync pytest" in test_job
    assert "Render Copier template" in workflow
    assert 'python-version: ["3.11", "3.12", "3.13", "3.14"]' in workflow
    assert (REPOSITORY_ROOT / ".github/renovate.json").is_file()


def test_generated_release_stages_validated_artifacts_across_minimal_permissions() -> (
    None
):
    workflow = (REPOSITORY_ROOT / "template/.github/workflows/release.yml").read_text(
        encoding="utf-8"
    )

    assert "permissions: {}" in workflow
    assert workflow.count("contents: read") == 1
    assert workflow.count("id-token: write") == 1
    assert workflow.count("contents: write") == 1
    assert 'git cat-file -t "refs/tags/$GITHUB_REF_NAME"' in workflow
    assert 'git merge-base --is-ancestor "$GITHUB_SHA" "origin/main"' in workflow
    assert "uv run --no-sync ruff check" in workflow
    assert "uv run --no-sync basedpyright" in workflow
    assert "uv run --no-sync pytest" in workflow
    assert "uv build --no-sources" in workflow
    assert "TWINE_VERSION" not in workflow
    assert "twine check" not in workflow
    assert "wheel.testzip()" in workflow
    assert 'tarfile.open(sdist_path, "r:gz")' in workflow
    assert workflow.count("actions/upload-artifact@") == 1
    assert workflow.count("actions/download-artifact@") == 2
    assert "release-${{ github.sha }}" in workflow
    assert "uv publish --trusted-publishing always" in workflow
    assert "needs: [validate, publish-pypi]" in workflow
    assert 'gh release create "$RELEASE_TAG"' in workflow
    assert "--verify-tag" in workflow
    assert "orhun/git-cliff-action" not in workflow
    assert "softprops/action-gh-release" not in workflow

    validate = workflow.index("  validate:")
    publish = workflow.index("  publish-pypi:")
    github_release = workflow.index("  github-release:")
    assert validate < publish < github_release
    assert workflow.index("Validate distribution artifacts") < workflow.index(
        "Publish with PyPI Trusted Publishing"
    )


def test_generated_renovate_uses_rebase_for_uv_updates() -> None:
    configuration = json.loads(
        (REPOSITORY_ROOT / "template/.github/renovate.json").read_text(encoding="utf-8")
    )

    assert "automergeType" not in configuration
    assert configuration["automergeStrategy"] == "rebase"
    assert configuration["platformAutomerge"] is False
    assert {
        "description": "Automerge uv patch updates after required checks pass",
        "matchPackageNames": ["astral-sh/uv"],
        "matchUpdateTypes": ["patch"],
        "automerge": True,
    } in configuration["packageRules"]
    assert {
        "description": "Require manual review for uv compatibility migrations",
        "matchPackageNames": ["astral-sh/uv"],
        "matchUpdateTypes": ["minor", "major"],
        "automerge": False,
    } in configuration["packageRules"]
