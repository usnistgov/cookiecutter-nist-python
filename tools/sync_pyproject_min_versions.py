"""Sync minimum versions to those in requirements/lock/uvx-tools.txt"""
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "packaging>=26.2",
#     "requirements-parser>=0.13.0",
# ]
# ///

from __future__ import annotations

import re
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Sequence


VERSION_PATTERN = r"""
    v?+                                                   # optional leading v
    (?a:
        (?:(?P<epoch>[0-9]+)!)?+                          # epoch
        (?P<release>[0-9]+(?:\.[0-9]+)*+)                 # release segment
        (?P<pre>                                          # pre-release
            [._-]?+
            (?P<pre_l>alpha|a|beta|b|preview|pre|c|rc)
            [._-]?+
            (?P<pre_n>[0-9]+)?
        )?+
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [._-]?
                (?P<post_l>post|rev|r)
                [._-]?
                (?P<post_n2>[0-9]+)?
            )
        )?+
        (?P<dev>                                          # dev release
            [._-]?+
            (?P<dev_l>dev)
            [._-]?+
            (?P<dev_n>[0-9]+)?
        )?+
    )
    (?a:\+
        (?P<local>                                        # local version
            [a-z0-9]+
            (?:[._-][a-z0-9]+)*+
        )
    )?+
"""


def _get_versions_from_requirements(
    requirements_path: Path | None,
) -> dict[str, str]:
    if requirements_path is None:
        return {}

    from requirements import parse

    versions: dict[str, str] = {}
    with requirements_path.open(encoding="utf-8") as f:
        for requirement in parse(f):
            name = cast("str", requirement.name)
            versions[name] = requirement.specs[0][-1]
    return versions


def _get_options(argv: Sequence[str] | None = None) -> tuple[Path, list[Path]]:
    parser = ArgumentParser(description=__doc__)
    _ = parser.add_argument(
        "-r",
        "--requirements",
        default="requirements/lock/uvx-tools.txt",
        type=Path,
    )
    _ = parser.add_argument("paths", nargs="+", type=Path)

    opts = parser.parse_args(argv)

    return opts.requirements, opts.paths


def _process_path(path: Path, versions: dict[str, str]) -> str:
    out = path.read_text(encoding="utf-8")
    for package, version in versions.items():
        out = re.sub(
            rf'"{package}(?P<extras>.*?>=)' + VERSION_PATTERN + '(?P<markers>.*)"',
            rf'"{package}\g<extras>{version}\g<markers>"',
            out,
            flags=re.VERBOSE,
        )

    return out


def main(argv: Sequence[str] | None = None) -> bool:
    """Main function"""
    requirements_path, paths = _get_options(argv)

    versions = _get_versions_from_requirements(requirements_path)

    for path in paths:
        out = _process_path(path, versions)
        _ = path.write_text(out, encoding="utf-8")

    return False


if __name__ == "__main__":
    raise SystemExit(main())
