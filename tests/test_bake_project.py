from pathlib import Path
import pytest

from utils import run_inside_dir

import logging

logger = logging.getLogger(__name__)


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


# @pytest.mark.create
def test_baked_create(example_path: Path) -> None:
    logging.info("in directory {}".format(Path.cwd()))
    assert Path.cwd().resolve() == example_path.resolve()


def test_baked_version(example_path: Path) -> None:
    py = get_python_version()
    if py == "3.10":
        run_inside_dir(f"nox -s update-version-scm", example_path)


# @pytest.mark.test
def test_baked_test(example_path: Path) -> None:
    py = get_python_version()
    run_inside_dir(f"nox -s test-venv-{py}", example_path)


# @pytest.mark.lint
def test_baked_lint(example_path: Path) -> None:
    py = get_python_version()

    if py == "3.10":
        run_inside_dir(f"git add .", example_path)
        try:
            code = run_inside_dir(f"nox -s lint", example_path)
        except Exception as error:
            logging.info(f"git diff")
            run_inside_dir(f"git diff", example_path)
            raise error


# @pytest.mark.docs
def test_baked_docs(example_path: Path) -> None:
    py = get_python_version()

    if py == "3.10":
        run_inside_dir(f"nox -s docs-venv -- -d symlink build", example_path)


# @pytest.mark.typing
def test_baked_typing(example_path: Path) -> None:
    py = get_python_version()

    if py == "3.10":
        run_inside_dir(f"nox -s typing-venv-{py}", example_path)
