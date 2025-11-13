"""
Update minimum value for python-version in `tool.uv.dependency-groups` table.

By default, set value to `>=python_version` with `python_version` taken from `.python-version` file.
"""
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "tomlkit",
# ]
# ///

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any


def main(args: Sequence[str] | None = None) -> None:
    """Main program."""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--python-version", "-p", help="Minimum python version", default=None
    )
    parser.add_argument(
        "--python-version-file",
        "-f",
        help="Text file with python version",
        default=".python-version",
    )
    options = parser.parse_args(args)

    python_version: str
    if options.python_version:
        python_version = options.python_version
    else:
        python_version = (
            Path(options.python_version_file).read_text(encoding="utf-8").strip()
        )

    python_min_version = f">={python_version}"

    from tomlkit.toml_file import TOMLFile

    toml = TOMLFile("pyproject.toml")

    data: dict[str, Any] = toml.read()

    dependency_groups: dict[str, Any] = data["tool"]["uv"]["dependency-groups"]  # pyright: ignore[reportIndexIssue, reportAssignmentType]

    for k, v in dependency_groups.items():
        if "requires-python" in v:
            dependency_groups[k]["requires-python"] = python_min_version

    toml.write(data)


if __name__ == "__main__":
    raise SystemExit(main())
