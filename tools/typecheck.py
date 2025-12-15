"""
Interface to type checkers (mypy, (based)pyright, ty, pyrefly) to handle python-version and python-executable.

This allows for running centrally installed (or via uvx) type checkers against a given virtual environment.
"""
# pylint: disable=duplicate-code

from __future__ import annotations

import logging
import os
import shlex
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


FORMAT = "[%(name)s - %(levelname)s] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
logger = logging.getLogger("typecheck")


# * Utilities -----------------------------------------------------------------
def _setup_logging(
    verbosity: int = 0,
) -> None:  # pragma: no cover
    """Setup logging."""
    level_number = max(0, logging.WARNING - 10 * verbosity)
    logger.setLevel(level_number)

    # Silence noisy loggers
    logging.getLogger("sh").setLevel(logging.WARNING)


# * Runner --------------------------------------------------------------------
def _do_run(
    *args: str,
    env: Mapping[str, str] | None = None,
    dry_run: bool = False,
) -> int:
    import subprocess

    cleaned_args = [*(os.fsdecode(arg) for arg in args)]
    full_cmd = shlex.join(cleaned_args)
    logger.info("Running %s", full_cmd)

    if dry_run:
        return 0

    r = subprocess.run(cleaned_args, check=False, env=env)

    if returncode := r.returncode:
        logger.error("Command %s failed with exit code %s", full_cmd, returncode)
        # msg = f"Returned code {returncode}"  # noqa: ERA001
        # raise RuntimeError(msg)  # noqa: ERA001
    return returncode


def _is_pyright_like(checker: str) -> bool:
    return checker in {"pyright", "basedpyright"}


def _get_python_flags(
    checker: str,
    python_version: str,
    python_executable: str,
) -> tuple[str, ...]:
    if checker == "pylint":
        return ()

    if _is_pyright_like(checker):
        python_flag = "pythonpath"
    elif checker == "ty":
        python_flag = "python"
    elif checker == "pyrefly":
        python_flag = "python-interpreter-path"
    elif checker == "mypy":
        # default to mypy
        python_flag = "python-executable"
    else:
        msg = f"Unknown checker {checker}"
        raise ValueError(msg)

    version_flag = "pythonversion" if _is_pyright_like(checker) else "python-version"

    check_subcommand = ["check"] if checker in {"ty", "pyrefly"} else []

    if checker == "ty":
        # ty prefers `--python` flag pointing to environonmentf
        python_executable = str(Path(python_executable).parent.parent)

    return (
        *check_subcommand,
        f"--{python_flag}={python_executable}",
        f"--{version_flag}={python_version}",
    )


def _run_checker(
    checker: str,
    *args: str,
    python_version: str,
    python_executable: str,
    constraints: list[Path],
    dry_run: bool = False,
    use_uvx: bool = True,
) -> int:
    checker, *checker_args = shlex.split(checker)

    python_flags = _get_python_flags(checker, python_version, python_executable)

    uvx_args = (
        (
            "uvx",
            *(f"--constraints={c}" for c in constraints),
            *(["--with", "orjson"] if checker == "mypy" else []),
        )
        if use_uvx
        else ()
    )

    return _do_run(
        *uvx_args,
        checker,
        *python_flags,
        *checker_args,
        *args,
        dry_run=dry_run,
    )


# * Application ---------------------------------------------------------------
def get_parser() -> ArgumentParser:
    """Get argparser."""
    parser = ArgumentParser(description="Run executable using uvx.")
    _ = parser.add_argument(
        "--python-executable",
        dest="python_executable",
        default=None,  # Path(sys.executable),
        type=Path,
        help="""
        Path to python executable. Defaults to ``sys.executable``. This is
        passed to `--python-executable` in mypy and `--pythonpath` in (based)pyright.
        """,
    )
    _ = parser.add_argument(
        "--python-version",
        dest="python_version",
        default=None,
        type=str,
        help="""
        Python version (x.y) to typecheck against. Defaults to
        ``{sys.version_info.major}.{sys.version_info.minor}``. This is passed
        to ``--pythonversion`` in pyright and ``--python-version`` otherwise.
        """,
    )
    _ = parser.add_argument(
        "-c",
        "--constraints",
        dest="constraints",
        default=[],
        action="append",
        type=Path,
        help="Requirements (requirements.txt) specs for checker.  Can specify multiple times.",
    )
    _ = parser.add_argument(
        "-v",
        "--verbose",
        dest="verbosity",
        action="count",
        default=0,
        help="Set verbosity level.  Pass multiple times to up level.",
    )
    _ = parser.add_argument(
        "-x",
        "--checker",
        dest="checkers",
        default=[],
        action="append",
        help="Type checker to use.",
    )
    _ = parser.add_argument(
        "--allow-errors",
        action="store_true",
    )
    _ = parser.add_argument(
        "--dry-run",
        action="store_true",
    )
    _ = parser.add_argument(
        "--no-uv",
        action="store_true",
    )
    _ = parser.add_argument(
        "args",
        type=str,
        nargs="*",
        default=[],
        help="extra arguments to checker(s)",
    )

    return parser


def main(args: Sequence[str] | None = None) -> int:
    """Main script."""
    parser = get_parser()
    options = parser.parse_args(args)

    _setup_logging(options.verbosity)

    python_version = (
        options.python_version or f"{sys.version_info.major}.{sys.version_info.minor}"
    )
    python_executable = options.python_executable or sys.executable

    logger.debug("checkers: %s", options.checkers)
    logger.debug("args: %s", options.args)

    code = 0
    for checker in options.checkers:
        code += _run_checker(
            checker,
            *options.args,
            python_version=python_version,
            python_executable=python_executable,
            constraints=options.constraints,
            dry_run=options.dry_run,
            use_uvx=not options.no_uv,
        )

    return 0 if options.allow_errors else code


if __name__ == "__main__":
    raise SystemExit(main())
