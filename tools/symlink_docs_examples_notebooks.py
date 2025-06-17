"""
Symlink notebooks docs/examples/usage/... -> examples/usage/...

Intended for use with pre-commit.
"""

from __future__ import annotations

import logging
import os
import shutil
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Sequence

FORMAT = "[%(name)s - %(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger("symlink_docs_examples_notebooks")


def _usage_paths(path: Path) -> Iterator[Path]:
    with path.open("r") as f:
        for line in f:
            if line.startswith("usage/"):
                yield Path(line.strip())


def _get_target_path(
    usage_path: Path,
    prefix_path: Path | None = None,
    exts: Sequence[str] = (".md", ".ipynb"),
) -> Path:
    if prefix_path is None:
        prefix_path = Path("./examples")

    path = Path(prefix_path) / Path(usage_path)

    if not all(ext.startswith(".") for ext in exts):
        msg = "Bad extensions.  Should start with '.'"
        raise ValueError(msg)

    if path.exists():
        return path

    for ext in exts:
        p = path.with_suffix(ext)
        if p.exists():
            return p

    msg = f"no path found for base {path}"
    raise ValueError(msg)


def _create_doc_examples_symlinks(
    paths: Iterable[Path],
    example_path: Path,
    clean: bool = True,
) -> None:
    paths = list(paths)
    if clean:
        for path in {p.parent / "usage" for p in paths}:
            logger.info("removing %s", path)
            shutil.rmtree(path, ignore_errors=True)

    # read usage lines
    for path in paths:
        for usage_path in _usage_paths(path):
            target = _get_target_path(usage_path, prefix_path=example_path)
            link = path.parent / usage_path.parent / target.name

            if link.exists():
                link.unlink()

            link.parent.mkdir(parents=True, exist_ok=True)

            target_rel = os.path.relpath(target, start=link.parent)
            logger.info("linking %s -> %s", target_rel, link)

            link.symlink_to(target_rel)


def main(args: Sequence[str] | None = None) -> int:
    """Main script"""
    parser = ArgumentParser()
    parser.add_argument(
        "--example-path",
        type=Path,
        default="./examples",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="default is to clean out `dos_example_path / usage`.  Pass this to skip clean.",
    )
    opts = parser.parse_args(args)

    _create_doc_examples_symlinks(
        Path("./docs/examples").glob("**/*.md"),
        example_path=opts.example_path,
        clean=not opts.no_clean,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
