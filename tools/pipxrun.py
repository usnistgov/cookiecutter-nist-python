"""
A script to invoke utilities from either pipx or from local installs.

I got tired of installing mypy/pyright in a million venvs. I got around this
for pyright using a central install and running in an activated venv. You can
do likewise with mypy, by passing `--python-executable`. I got the bright idea
to use `pipx` to manage mypy and pyright. But when working from my own machine,
I'd already have the type checkers installed centrally. This script automates
running these tools. It does the following:

* Optionally can set the `specification` (i.e., "mypy==1.2.3...", etc)
* Will check if the specification is installed. If it is, use it (unless pass
 `-x`). Otherwise, run the command via `pipx` (something like `pipx run
 mypy==1.2.3...`)
* You can set the specifications from a `requirements.txt` file. So you can use
  tools like `pip-compile` to manage the versions.
* Makes the `--python-executable` and `--pythonpath` flags to mypy and pyright
  the same. Defaults to using `sys.executable` from the python running this
* Also sets `--python-version` and `--pythonversion` in mypy and pyright
* For other tools, just run them from pipx or installed.
"""

from __future__ import annotations

import logging
import re
import shlex
import subprocess
import sys
import textwrap
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from packaging.requirements import Requirement
from packaging.version import Version

if TYPE_CHECKING:
    import argparse
    from typing import Iterable, Iterator, Sequence


class CustomFormatter(logging.Formatter):
    """Custom formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Custom format."""
        msg = textwrap.fill(
            super().format(record),
            width=_max_output_width(),
            subsequent_indent=" " * 4,
            break_long_words=False,
            replace_whitespace=False,
            drop_whitespace=False,
            break_on_hyphens=False,
        ).replace("\n", "\\\n")
        if msg.endswith("\\\n"):
            msg = msg.rstrip("\\\n") + "\n"

        return msg


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    CustomFormatter(
        "{name}({levelname}): {message}",
        style="{",
    )
)

logging.basicConfig(
    level=logging.WARNING,
    handlers=[
        handler,
    ],
)
logger = logging.getLogger("pipxrun")


@lru_cache
def _comment_re() -> re.Pattern[str]:
    return re.compile(r"(^|\s+)#.*$")


def _run_command(command: Sequence[str], dry: bool = False) -> int:
    logger.info("Running %s\n", " ".join(command))
    if not dry:
        r = subprocess.run(command, check=False)
        return r.returncode
    return 0


@lru_cache
def _max_output_width() -> int:
    import shutil

    width = shutil.get_terminal_size((80, 20)).columns

    min_width, max_width = 20, 150
    if width > max_width:
        width = max_width
    if width < min_width:
        width = min_width
    return width


def _print_header(name: str = "") -> None:
    if logger.isEnabledFor(logging.WARNING):
        fmt = f"{{:=<{_max_output_width()}}}"
        if name:
            name = f"= {name} "
        print(fmt.format(name))  # noqa: T201


@lru_cache
def _get_command_version(name: str, path: str) -> Version:
    # Note that this version is faster than
    # Calling subprocess to get --version (see bottom of file).
    # But it might break on windows...

    with Path(path).open() as f:
        python_executable = f.readline().strip().replace("#!", "")

    return Version(
        subprocess.check_output(
            [
                python_executable,
                "-c",
                f"from importlib.metadata import version; print(version('{name}'))",
            ]
        )
        .decode()
        .strip()
    )


def _parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    """Get parser."""
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description="Run executable using pipx or from installed if matches specification."
    )
    parser.add_argument(
        "--python-executable",
        dest="python_executable",
        default=None,  # Path(sys.executable),
        type=Path,
        help="""
        Path to python executable. Defaults to ``sys.executable``. This is
        passed to `--python-executable` in mypy and `--pythonpath` in pyright.
        """,
    )
    parser.add_argument(
        "--python-version",
        dest="python_version",
        default=None,
        type=str,
        help="""
        Python version (x.y) to typecheck against. Defaults to
        ``{sys.version_info.major}.{sys.version_info.minor}``. This is passed
        to ``--python-version`` and ``--pythonversion`` in mypy and pyright.
        """,
    )
    parser.add_argument(
        "-c",
        "--command",
        dest="commands",
        default=[],
        action="append",
        type=str,
        help="""
        Checkers command. This can include extra flags to the checker. This can
        also be passed multiple times for multiple checkers. This can also
        include a Requirement specification, which overrides any specification
        from ``--requirement`` or ``--spec``. For example,
        ``--command='mypy==1.8.0 --no-incremental' -c pyright``
        """,
    )
    parser.add_argument(
        "-r",
        "--requirement",
        dest="requirements",
        default=[],
        action="append",
        type=Path,
        help="Requirements (requirements.txt) specs for checker.  Can specify multiple times.",
    )
    parser.add_argument(
        "-s",
        "--spec",
        dest="specs",
        default=[],
        action="append",
        type=Requirement,
        help="""
        Package specification. Can pass multiple times. Overrides specs read
        from ``--requirements``. For example, ``--spec 'mypy==1.2.3'``.
        """,
    )
    parser.add_argument("--dry", action="store_true", help="Do dry run")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbosity",
        action="count",
        default=0,
        help="Set verbosity level.  Pass multiple times to up level.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        help="Lower verbosity level.  Pass multiple times to up level.",
    )
    parser.add_argument(
        "-x",
        "--pipx",
        dest="pipx_only",
        action="store_true",
        help="Always use pipx to run the commands (No local fallback)",
    )
    parser.add_argument(
        "files", type=str, default=[], nargs="*", help="Optional files to check."
    )

    options = parser.parse_args() if args is None else parser.parse_args(args)

    if not options.commands:
        parser.print_usage()

    return options


def _set_verbosity_level(logger: logging.Logger, verbosity: int) -> None:
    """Set verbosity level."""
    level_number = max(0, logging.WARNING - 10 * verbosity)
    logger.setLevel(level_number)


def _parse_requirements(requirements: Path) -> Iterator[Requirement]:
    comment_re = _comment_re()

    def ignore_comments(lines: Iterable[str]) -> Iterator[str]:
        """Strips comments and filter empty lines."""
        for line in lines:
            if line_formatted := comment_re.sub("", line).strip():
                yield line_formatted

    with requirements.open() as f:
        yield from map(Requirement, ignore_comments(f))


class Command:
    """Class to handle commands."""

    def __init__(
        self, name: str, args: Iterable[str], spec: Requirement | None = None
    ) -> None:
        self.name = name
        self.args = list(args)
        self.spec = spec

    @classmethod
    def from_command(cls, command: str) -> Command:
        """Create from command iterable"""
        name, *args = shlex.split(command)
        spec = Requirement(name)
        return cls(
            name=spec.name,
            args=args,
            spec=spec if spec.specifier else None,
        )

    def assign_spec(self, spec: Requirement | None, override: bool = False) -> Command:
        """Update spec from specs dict."""
        if spec and (override or not self.spec):
            return type(self)(name=self.name, args=self.args, spec=spec)
        return self

    def _get_python_flags(
        self, python_executable: Path, python_version: str
    ) -> list[str]:
        if not python_executable:
            return []

        if self.name == "mypy":
            return [
                f"--python-executable={python_executable}",
                f"--python-version={python_version}",
            ]
        if self.name == "pyright":
            return [
                f"--pythonpath={python_executable}",
                f"--pythonversion={python_version}",
            ]

        logger.debug("Unknown command %s", self.name)
        return []

    @staticmethod
    def _get_pipx_flags(verbosity: int) -> list[str]:
        if verbosity > 0:
            return [f"-{'v' * verbosity}"]
        if verbosity < 0:
            return [f"-{'q' * -verbosity}"]
        return []

    def run(
        self,
        python_executable: Path,
        python_version: str,
        files: Iterable[str],
        dry: bool = False,
        verbosity: int = 0,
        pipx_only: bool = False,
    ) -> int:
        """Run the command"""
        from shutil import which

        _print_header(self.name)

        commands: list[str] = []
        if not pipx_only and (exe_path := which(self.name)):
            if self.spec is None:
                logger.info("Using local %s at %s", self.name, exe_path)
                commands = [exe_path]
            elif (
                exe_version := _get_command_version(name=self.name, path=exe_path)
            ) and exe_version in self.spec.specifier:
                logger.info(
                    "Using local %s with version %s at %s",
                    self.spec,
                    exe_version,
                    exe_path,
                )
                commands = [exe_path]

        if not commands:
            logger.warning("Using pipx run %s", self.spec or self.name)
            commands = [
                "pipx",
                "run",
                *self._get_pipx_flags(verbosity=verbosity),
                *([f"--spec={self.spec}"] if self.spec else []),
                self.name,
            ]

        commands = [
            *commands,
            *self._get_python_flags(python_executable, python_version),
            *self.args,
            *files,
        ]

        code = _run_command(
            commands,
            dry=dry,
        )

        logger.info("%s exitcode: %s\n", self.name, code)

        return code


def _get_running_python_parameters() -> tuple[str, str]:
    python_version = "{}.{}".format(*sys.version_info[:2])
    return sys.executable, python_version


def main(args: Sequence[str] | None = None) -> int:
    """Main script."""
    if not (options := _parse_args(args)).commands:
        return 0

    # setup
    _set_verbosity_level(logger, options.verbosity - options.quiet)

    python_executable, python_version = _get_running_python_parameters()
    logger.info("Running with python %s at %s", python_version, python_executable)

    commands = [Command.from_command(command=command) for command in options.commands]
    command_names = [command.name for command in commands]

    # specs from requirements
    specs: dict[str, Requirement] = {
        req.name: req
        for requirement in options.requirements
        for req in _parse_requirements(requirement)
        if req.name in command_names
    }
    # specs for passed specs
    specs.update({spec.name: spec for spec in options.specs})

    # update command specs
    commands = [command.assign_spec(specs.get(command.name)) for command in commands]

    return sum(
        command.run(
            python_executable=options.python_executable or Path(python_executable),
            python_version=options.python_version or python_version,
            dry=options.dry,
            verbosity=options.verbosity - options.quiet - 2,
            pipx_only=options.pipx_only,
            files=options.files,
        )
        for command in commands
    )


if __name__ == "__main__":
    sys.exit(main())


# Alternative method to get command version...
# @lru_cache
# def _version_re() -> re.Pattern[str]:
#     return re.compile(
#         r"\b([1-9][0-9]*!)?(0|[1-9][0-9]*)"
#         r"(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))"
#         r"?(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?\b"
#     )
#
#
# @lru_cache
# def _get_command_version(command: str, flag: str = "--version") -> Version | None:
#     version_search = _version_re().search(
#         subprocess.check_output([command, flag])
#         .decode()
#         .strip()
#     )
#     if version_search:
#         return Version(version_search.group(0))
#     return None
#
#
# def _get_site(python_executable: str | Path) -> str:
#     """Getesite-packages for python path (trying to make pytype work)"""
#     return (
#         subprocess.check_output(
#             [
#                 python_executable,
#                 "-c",
#                 "import sysconfig; print(sysconfig.get_paths()['purelib'])",
#             ]
#         )
#         .decode()
#         .strip()
#     )
