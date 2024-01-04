from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import pytest
from utils import run_inside_dir

logger = logging.getLogger(__name__)

DEFAULT_PYTHON = "3.11"


# * Actual testing
# ** Utilities


def _add_extras(x: list[str], extras: str | Iterable[str] | None) -> list[str]:
    if extras is None:
        out = x
    elif isinstance(extras, str):
        out = [*x, extras]
    else:
        out = x + list(extras)

    return out


def check_directory(
    path: str | Path,
    extra_files: str | Iterable[str] | None = None,
    extra_directories: str | Iterable[str] | None = None,
    files: list[str] | None = None,
    directories: list[str] | None = None,
    ignore_paths: list[str] | None = None,
) -> None:
    """Check path for files and directories"""
    path = Path(path)

    if ignore_paths is None:
        ignore_paths = ["__pycache__"]

    if files is None:
        files = [
            ".editorconfig",
            ".gitignore",
            ".markdownlint.yaml",
            ".pre-commit-config.yaml",
            ".prettierrc.yaml",
            "pyproject.toml",
            "noxfile.py",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "LICENSE",
            "MANIFEST.in",
            "Makefile",
            "README.md",
            "AUTHORS.md",
        ]

    if directories is None:
        directories = [
            # These are added by the example creation
            ".nox",
            ".git",
            # These are created from the template
            ".github",
            "changelog.d",
            "config",
            "docs",
            "examples",
            "requirements",
            "src",
            "tests",
            "tools",
        ]

    files = _add_extras(files, extra_files)
    directories = _add_extras(directories, extra_directories)

    found_files: list[str] = []
    found_directories: list[str] = []

    for p in Path(path).iterdir():
        if p.name in ignore_paths:
            continue

        if p.is_dir():
            found_directories.append(p.name)
        else:
            found_files.append(p.name)

    assert set(files) == set(found_files)
    assert set(directories) == set(found_directories)


def get_python_version() -> str:
    import sys

    return "{}.{}".format(*sys.version_info[:2])


# ** fixtures
# @pytest.mark.create
def test_baked_create(example_path: Path) -> None:
    logging.info(f"in directory {Path.cwd()}")
    assert Path.cwd().resolve() == example_path.resolve()

    extra_files = (
        [".copier-answers.yml"] if "copier" in str(example_path.name) else None
    )

    check_directory(path=example_path, extra_files=extra_files)


@pytest.mark.disable()
def test_baked_version(example_path: Path) -> None:
    py = get_python_version()

    if py == "DEFAULT_PYTHON":
        run_inside_dir("nox -s build -- ++build version", example_path)


# @pytest.mark.test
def test_baked_test(example_path: Path, nox_opts: str, nox_session_opts: str) -> None:
    py = get_python_version()

    run_inside_dir(f"nox {nox_opts} -s test-{py} -- {nox_session_opts}", example_path)


# @pytest.mark.lint
def test_baked_lint(example_path: Path, nox_opts: str, nox_session_opts: str) -> None:
    py = get_python_version()

    if py == DEFAULT_PYTHON:
        try:
            run_inside_dir(
                f"nox {nox_opts} -s lint -- {nox_session_opts}", example_path
            )
        except Exception as error:
            logging.info("git diff")
            run_inside_dir("git diff", example_path)
            raise error


# @pytest.mark.docs
def test_baked_docs(example_path: Path, nox_opts: str, nox_session_opts: str) -> None:
    py = get_python_version()

    if py == DEFAULT_PYTHON:
        run_inside_dir(
            f"nox {nox_opts} -s docs -- +d symlink build {nox_session_opts}",
            example_path,
        )


# @pytest.mark.typing
def test_baked_typing(example_path: Path, nox_opts: str, nox_session_opts: str) -> None:
    py = get_python_version()

    run_inside_dir(
        f"nox {nox_opts} -s typing-{py} -- +m clean mypy pyright {nox_session_opts}",
        example_path,
    )


def test_baked_mypystrict(
    example_path: Path, nox_opts: str, nox_session_opts: str
) -> None:
    py = get_python_version()

    if py == DEFAULT_PYTHON:
        run_inside_dir(
            f"nox {nox_opts} -s typing-{py} -- +m clean ++typing-run-internal 'mypy --strict' {nox_session_opts}",
            example_path,
        )


def test_baked_notebook(
    example_path: Path, nox_opts: str, nox_session_opts: str
) -> None:
    py = get_python_version()

    if py == DEFAULT_PYTHON:
        run_inside_dir(
            f"nox {nox_opts} -s typing-{py} -- +m clean typing-notebook {nox_session_opts}",
            example_path,
        )
        run_inside_dir(
            f"nox {nox_opts} -s test-notebook -- {nox_session_opts}",
            example_path,
        )
