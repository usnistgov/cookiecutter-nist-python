"""Create requirements/lock/*.txt files from requirements/*.txt files."""

from __future__ import annotations

import logging
import shlex
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

FORMAT = "[%(name)s - %(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger("clean_kernelspec")

if sys.version_info < (3, 11):
    msg = "python>3.11 required"
    raise RuntimeError(msg)


def _get_min_python_version() -> str:
    with Path("pyproject.toml").open("rb") as f:
        import tomllib

        return next(  # type: ignore[no-any-return]
            c.split()[-1]
            for c in tomllib.load(f)["project"]["classifiers"]
            if c.startswith("Programming Language :: Python :: 3.")
        )


def _get_default_version() -> str:
    return Path(".python-version").read_text(encoding="utf-8").strip()


def _lock_files(
    paths: Iterable[Path],
    min_python_version: str,
    default_python_version: str,
    pip_compile_config: Path,
    upgrade: bool = False,
) -> None:
    from subprocess import check_call

    for path in paths:
        python_version = (
            min_python_version
            if path.name
            in {"test.txt", "test-extras.txt", "typecheck.txt", "uvx-tools.txt"}
            else default_python_version
        )

        lockpath = path.parent / "lock" / path.name

        options = [
            "uv",
            "pip",
            "compile",
            "--universal",
            f"--config-file={pip_compile_config}",
            "-q",
            # don't include dependencies for uvx-tools
            *(
                ["--no-deps", "--no-strip-extras"]
                if path.name == "uvx-tools.txt"
                else []
            ),
            "--python-version",
            python_version,
            *(["--upgrade"] if upgrade else []),
            str(path),
            "-o",
            str(lockpath),
        ]

        logger.info(shlex.join(options))
        check_call(options)


def main(args: Sequence[str] | None = None) -> int:
    """Main script."""
    # pylint: disable=duplicate-code
    parser = ArgumentParser()
    parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Upgrade requirements",
    )
    parser.add_argument(
        "--pip-compile-config",
        default="./requirements/uv.toml",
        type=Path,
        help="Config file for locking.",
    )
    parser.add_argument(
        "--all",
        dest="all_",
        action="store_true",
        help="Run on all files.",
    )
    parser.add_argument(
        "paths",
        type=Path,
        nargs="*",
    )

    opts = parser.parse_args(args)

    _lock_files(
        Path("./requirements").glob("*.txt") if opts.all_ else opts.paths,
        min_python_version=_get_min_python_version(),
        default_python_version=_get_default_version(),
        upgrade=opts.upgrade,
        pip_compile_config=opts.pip_compile_config,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
