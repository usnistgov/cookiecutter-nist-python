from contextlib import contextmanager
import shlex
import os
import subprocess
from cookiecutter.utils import rmtree

from pathlib import Path

import pytest

CACHED_EXAMPLES_PATH = (Path(__file__).parent / ".." / "cached_examples").resolve()


@contextmanager
def inside_dir(dirpath):
    """
    Execute code from inside the given directory
    :param dirpath: String, path of the directory the command is being run.
    """
    old_path = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


def run_inside_dir(command, dirpath):
    """
    Run a command from inside a given directory, returning the exit status
    :param command: Command that will be executed
    :param dirpath: String, path of the directory the command is being run.
    """
    with inside_dir(dirpath):
        return subprocess.check_call(shlex.split(command))


# * Actual testing
# ** Utilities
def check_directory(
    path, extra_files=None, extra_directories=None, files=None, directories=None
):
    """Check path for files and directories"""
    path = Path(path)

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

    def _add_extras(x, extras):
        if extras is None:
            return x
        elif isinstance(extras, str):
            return x + [extras]
        else:
            return x + list(extras)

    files = _add_extras(files, extra_files)
    directories = _add_extras(directories, extra_directories)

    found_files = []
    found_directories = []

    for p in Path(path).iterdir():
        if p.is_dir():
            found_directories.append(p.name)
        else:
            found_files.append(p.name)

    assert set(files) == set(found_files)
    assert set(directories) == set(found_directories)


def get_python_version():
    import sys

    return "{}.{}".format(*sys.version_info[:2])


def run_nox_tests(path, test=True, docs=True, lint=True):
    path = str(path)
    py = get_python_version()

    run_inside_dir("nox -s requirements", path)

    if test:
        run_inside_dir(f"nox -s test-venv-{py}", path)

    if lint:
        run_inside_dir("git init", path)
        run_inside_dir("git add .", path)
        run_inside_dir(f"nox -s lint", path)

    if docs and py == "3.10":
        run_inside_dir(f"nox -s docs-venv -- -d symlink build", path)


# ** fixtures
# @pytest.fixture
# def result_default(cookies):
#     return cookies.bake()


# ** tests
def test_bake_and_run_tests_default():
    project_path = CACHED_EXAMPLES_PATH / "testpackage-default"

    # test directory structure
    check_directory(project_path)

    # test nox
    run_nox_tests(project_path)


def test_bake_and_run_tests_with_furo(cookies):
    project_path = CACHED_EXAMPLES_PATH / "testpackage-furo"

    # test directory structure
    check_directory(project_path)

    # test nox
    run_nox_tests(project_path)


def test_bake_and_run_tests_with_typer(cookies):
    project_path = CACHED_EXAMPLES_PATH / "testpackage-typer"

    # test directory structure
    check_directory(project_path)

    # test nox
    run_nox_tests(project_path)
