from __future__ import annotations

import ast
import subprocess
import sys
import tarfile
import tomllib
import zipfile
from datetime import datetime
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def copy_result(
    template: Path,
    destination: Path,
    *answers: str,
) -> subprocess.CompletedProcess[str]:
    arguments = [
        sys.executable,
        "-m",
        "copier",
        "copy",
        "--defaults",
    ]
    for answer in answers:
        arguments.extend(("--data", answer))
    arguments.extend((str(template), str(destination)))
    return subprocess.run(arguments, check=False, text=True, capture_output=True)


def render_default(template: Path, destination: Path, *answers: str) -> None:
    result = copy_result(
        template,
        destination,
        "repo_owner=Misty02600",
        "repo_name=nonebot-plugin-example",
        "module_name=nonebot_plugin_example",
        *answers,
    )
    assert result.returncode == 0, result.stderr


def test_default_template_renders_a_nonebot_plugin(
    template_snapshot: Path, tmp_path: Path
) -> None:
    destination = tmp_path / "generated"
    year_before = datetime.now().year
    render_default(template_snapshot, destination)
    year_after = datetime.now().year

    assert (destination / ".copier-answers.yml").is_file()
    assert (destination / "src/nonebot_plugin_example").is_dir()
    assert not (destination / "template").exists()
    assert not (destination / "docs").exists()
    assert (destination / "tests/integration/__init__.py").read_bytes() == b""
    assert (destination / "tests/units/__init__.py").read_bytes() == b""
    with (destination / "pyproject.toml").open("rb") as file:
        pyproject = tomllib.load(file)
    assert "description" not in pyproject["project"]
    assert pyproject["project"]["license"] == "MIT"
    assert pyproject["project"]["license-files"] == ["LICENSE"]
    assert "commitizen>=4.1.0,<5.0.0" in pyproject["dependency-groups"]["dev"]
    assert "nb-cli>=1.7.0,<2.0.0" in pyproject["dependency-groups"]["dev"]
    assert "prek>=0.2.0,<1.0.0" in pyproject["dependency-groups"]["dev"]
    assert {"include-group": "lint"} in pyproject["dependency-groups"]["dev"]
    assert {"include-group": "test"} in pyproject["dependency-groups"]["dev"]
    assert {"include-group": "type"} in pyproject["dependency-groups"]["dev"]
    assert pyproject["dependency-groups"]["lint"] == ["ruff>=0.14.13,<1.0.0"]
    assert "pytest>=9.0.0,<10.0.0" in pyproject["dependency-groups"]["test"]
    assert pyproject["dependency-groups"]["type"] == ["basedpyright>=1.16.0,<2.0.0"]
    assert not {
        "basedpyright>=1.16.0,<2.0.0",
        "ruff>=0.14.13,<1.0.0",
    } & set(pyproject["dependency-groups"]["test"])
    assert "required-version" not in pyproject["tool"]["uv"]
    assert pyproject["tool"]["uv"]["build-backend"] == {
        "module-name": "nonebot_plugin_example"
    }

    pytest_configuration = (destination / "pytest.ini").read_text(encoding="utf-8")
    assert "pythonpath" not in pytest_configuration

    workflow = (destination / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert workflow.count("uv sync --only-group lint") == 1
    assert workflow.count("uv sync --no-dev --group type --all-extras") == 1
    assert workflow.count("uv sync --no-dev --group test") == 1
    pull_request_trigger = workflow.split("  pull_request:\n", 1)[1].split(
        "\npermissions:\n", 1
    )[0]
    assert "\n    paths:" not in pull_request_trigger
    assert "\n    paths-ignore:" not in pull_request_trigger
    assert (
        "concurrency:\n"
        "  group: ${{ github.workflow }}-"
        "${{ github.event.pull_request.number || github.run_id }}\n"
        "  cancel-in-progress: ${{ github.event_name == 'pull_request' }}\n"
    ) in workflow

    readme = (destination / "README.md").read_text(encoding="utf-8")
    assert "`just sync`：同步全部开发依赖组和所有可共同安装的 extras。" in readme
    assert "just bump" in readme
    assert "just push-release" not in readme

    license_text = (destination / "LICENSE").read_text(encoding="utf-8")
    assert any(
        f"Copyright (c) {year} Misty02600" in license_text
        for year in {year_before, year_after}
    )


def test_synced_project_exposes_cli_and_imports_installed_package(
    template_snapshot: Path,
    tmp_path: Path,
) -> None:
    destination = tmp_path / "synced-project"
    render_default(template_snapshot, destination)

    sync = subprocess.run(
        ("uv", "sync", "--all-groups", "--all-extras"),
        cwd=destination,
        check=False,
        text=True,
        capture_output=True,
    )
    assert sync.returncode == 0, sync.stderr

    cli = subprocess.run(
        ("uv", "run", "--no-sync", "nb", "--help"),
        cwd=destination,
        check=False,
        text=True,
        capture_output=True,
    )
    assert cli.returncode == 0, cli.stderr

    tests = subprocess.run(
        ("uv", "run", "--no-sync", "pytest"),
        cwd=destination,
        check=False,
        text=True,
        capture_output=True,
    )
    assert tests.returncode == 0, tests.stdout + tests.stderr


@pytest.mark.parametrize("module_name", ["class", "json", "_json"])
def test_template_rejects_unsafe_module_names(
    template_snapshot: Path,
    tmp_path: Path,
    module_name: str,
) -> None:
    result = copy_result(
        template_snapshot,
        tmp_path / f"invalid-{module_name}",
        "repo_owner=Misty02600",
        "repo_name=nonebot-plugin-example",
        f"module_name={module_name}",
    )

    assert result.returncode != 0
    assert "Python 关键字" in result.stderr or "标准库" in result.stderr


@pytest.mark.parametrize(
    ("answer", "expected_error"),
    [
        ("repo_owner=owner--name", "1 到 39 位"),
        ("repo_name=-invalid", "必须以字母或数字开头和结尾"),
        (f"repo_name={'a' * 101}", "1 到 100 位"),
        ("author_name=   ", "作者名不能为空"),
        ("author_email=not-an-email", "包含单个 @"),
    ],
)
def test_template_rejects_invalid_repository_and_author_answers(
    template_snapshot: Path,
    tmp_path: Path,
    answer: str,
    expected_error: str,
) -> None:
    answers = [
        "repo_owner=Misty02600",
        "repo_name=nonebot-plugin-example",
        "module_name=nonebot_plugin_example",
        "author_name=Template Author",
        "author_email=template@example.invalid",
    ]
    key = answer.partition("=")[0]
    answers = [
        candidate for candidate in answers if not candidate.startswith(f"{key}=")
    ]
    answers.append(answer)

    result = copy_result(
        template_snapshot,
        tmp_path / f"invalid-{key}",
        *answers,
    )

    assert result.returncode != 0
    assert expected_error in result.stderr


def test_template_accepts_repository_name_at_github_limit(
    template_snapshot: Path,
    tmp_path: Path,
) -> None:
    repo_name = "a" * 100
    destination = tmp_path / "maximum-repository-name"
    result = copy_result(
        template_snapshot,
        destination,
        "repo_owner=Misty02600",
        f"repo_name={repo_name}",
        "module_name=maximum_repository_name",
        "author_name=Template Author",
        "author_email=template@example.invalid",
    )

    assert result.returncode == 0, result.stderr
    with (destination / "pyproject.toml").open("rb") as file:
        assert tomllib.load(file)["project"]["name"] == repo_name


def test_author_identity_is_serialized_as_data(
    template_snapshot: Path,
    tmp_path: Path,
) -> None:
    author_name = 'Misty "Quoted"; $(Write-Output injected) \\ path'
    author_email = "misty+template@example.com"
    destination = tmp_path / "quoted-author"
    render_default(
        template_snapshot,
        destination,
        f"author_name={author_name}",
        f"author_email={author_email}",
    )

    with (destination / "pyproject.toml").open("rb") as file:
        configuration = tomllib.load(file)
    assert configuration["project"]["authors"] == [
        {"name": author_name, "email": author_email}
    ]

    source = (destination / "src/nonebot_plugin_example/__init__.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    metadata_call = next(
        node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "__plugin_meta__"
            for target in node.targets
        )
        and isinstance(node.value, ast.Call)
    )
    extra = next(
        keyword.value for keyword in metadata_call.keywords if keyword.arg == "extra"
    )
    assert ast.literal_eval(extra) == {"author": author_name}


def test_built_distributions_include_the_mit_license(
    template_snapshot: Path,
    tmp_path: Path,
) -> None:
    destination = tmp_path / "distribution"
    render_default(template_snapshot, destination)

    result = subprocess.run(
        ("uv", "build", "--no-sources"),
        cwd=destination,
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr

    wheels = list((destination / "dist").glob("*.whl"))
    sdists = list((destination / "dist").glob("*.tar.gz"))
    assert len(wheels) == 1
    assert len(sdists) == 1

    with zipfile.ZipFile(wheels[0]) as wheel:
        wheel_files = wheel.namelist()
        metadata_path = next(
            path for path in wheel_files if path.endswith(".dist-info/METADATA")
        )
        metadata_lines = wheel.read(metadata_path).decode("utf-8").splitlines()
        assert any(path.endswith(".dist-info/licenses/LICENSE") for path in wheel_files)
        assert "License-Expression: MIT" in metadata_lines
        assert "License-File: LICENSE" in metadata_lines

    with tarfile.open(sdists[0], "r:gz") as sdist:
        assert any(path.endswith("/LICENSE") for path in sdist.getnames())


def test_custom_module_name_builds_the_selected_package(
    template_snapshot: Path,
    tmp_path: Path,
) -> None:
    destination = tmp_path / "custom-module"
    result = copy_result(
        template_snapshot,
        destination,
        "repo_owner=Misty02600",
        "repo_name=nonebot-plugin-example",
        "module_name=custom_plugin",
    )
    assert result.returncode == 0, result.stderr

    build = subprocess.run(
        ("uv", "build", "--no-sources"),
        cwd=destination,
        check=False,
        text=True,
        capture_output=True,
    )
    assert build.returncode == 0, build.stderr

    with (destination / "pyproject.toml").open("rb") as file:
        configuration = tomllib.load(file)
    assert configuration["tool"]["uv"]["build-backend"] == {
        "module-name": "custom_plugin"
    }

    wheel = next((destination / "dist").glob("*.whl"))
    with zipfile.ZipFile(wheel) as archive:
        assert "custom_plugin/__init__.py" in archive.namelist()

    sdist = next((destination / "dist").glob("*.tar.gz"))
    with tarfile.open(sdist, "r:gz") as archive:
        assert any(
            name.endswith("/src/custom_plugin/__init__.py")
            for name in archive.getnames()
        )
