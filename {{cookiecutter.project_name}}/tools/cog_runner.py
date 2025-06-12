"""Script to run cog on files"""

from __future__ import annotations

import logging
import shlex
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence


FORMAT = "[%(name)s - %(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger("clean_kernelspec")


def _run_cog(
    files: Iterable[str],
    extras: Iterable[str],
    env: Mapping[str, str] | None = None,
) -> None:
    if env is not None:
        import os

        env = dict(os.environ, **env)

    command = [
        "uv",
        "run",
        *extras,
        "cog",
        "-rP",
        *files,
    ]

    logger.info(shlex.join(command))

    from subprocess import check_call

    check_call(command, env=env)


def _run_linters(
    files: Sequence[str],
    linters: Iterable[str],
) -> None:
    from subprocess import run

    for linter in linters:
        command = [
            "uvx",
            "--constraints=requirements/lock/uvx-tools.txt",
            "pre-commit",
            "run",
            linter,
            "--files",
            *files,
        ]

        logger.info(shlex.join(command))
        run(command, check=False)


def main(args: Sequence[str] | None = None) -> int:
    """Main script."""
    parser = ArgumentParser(description="run cog and linters")
    parser.add_argument(
        "--linter",
        dest="linters",
        action="append",
        default=[],
    )

    parser.add_argument(
        "files",
        nargs="+",
    )

    opts, extras = parser.parse_known_args(args)

    for path in map(Path, opts.files):
        if not path.exists():
            msg = f"{path} does not exist.  Remember that options should passed with --name=value and not --name value"
            raise ValueError(msg)

    logger.info("opts: %s", opts)
    logger.info("extras: %s", extras)

    _run_cog(
        opts.files,
        extras=extras,
        env={"COLUMNS": "90"},
    )

    _run_linters(
        opts.files,
        opts.linters,
    )

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
