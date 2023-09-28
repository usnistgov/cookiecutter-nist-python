from contextlib import contextmanager
import shlex
import os
import subprocess
from cookiecutter.utils import rmtree

from pathlib import Path



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


@contextmanager
def bake_in_temp_dir(cookies, *args, **kwargs):
    """
    Delete the temporal directory that is created when executing the tests
    :param cookies: pytest_cookies.Cookies,
        cookie to be baked and its temporal files will be removed
    """
    result = cookies.bake(*args, **kwargs)
    try:
        yield result
    finally:
        rmtree(str(result.project))


def run_inside_dir(command, dirpath):
    """
    Run a command from inside a given directory, returning the exit status
    :param command: Command that will be executed
    :param dirpath: String, path of the directory the command is being run.
    """
    with inside_dir(dirpath):
        return subprocess.check_call(shlex.split(command))


def check_output_inside_dir(command, dirpath):
    "Run a command from inside a given directory, returning the command output"
    with inside_dir(dirpath):
        return subprocess.check_output(shlex.split(command))

def project_info(result):
    """Get toplevel dir, project_slug, and project dir from baked cookies"""
    project_path = str(result.project)
    project_slug = os.path.split(project_path)[-1]
    project_dir = os.path.join(project_path, project_slug)
    return project_path, project_slug, project_dir


# * Actual testing
# ** Utilities
def check_directory(path, extra_files=None, extra_directories=None, files=None, directories=None):
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
        run_inside_dir(f"nox -s docs-venv -- -d symlink docs", path)

# ** fixtures
# @pytest.fixture
# def result_default(cookies):
#     return cookies.bake()



# ** tests
def test_bake_and_run_tests_default(cookies):
    result = cookies.bake()
    # test directory structure
    check_directory(result.project_path)

    # test nox
    run_nox_tests(result.project_path)





def test_bake_and_run_tests_with_furo(cookies):
    result = cookies.bake(extra_context={"sphinx_theme": "furo", "command_line_interface": "Click"})

    # test directory structure
    check_directory(result.project_path)

    # test nox
    run_nox_tests(result.project_path)


def test_bake_and_run_tests_with_typer(cookies):
    result = cookies.bake(extra_context={"command_line_interface": "Typer"})

    # test directory structure
    check_directory(result.project_path)

    # test nox
    run_nox_tests(result.project_path)
