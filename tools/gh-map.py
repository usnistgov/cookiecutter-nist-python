"""Run workflow over multiple repos."""
# /// script
# requires-python = ">=3.12"
# ///

# ruff:file-ignore[print, invalid-module-name]
from __future__ import annotations

import os
import shlex
import subprocess
from collections import ChainMap
from pathlib import Path
from typing import cast


def _get_repos(path: Path) -> list[str]:
    import tomllib

    return cast(
        "list[str]", tomllib.loads(path.read_text(encoding="utf-8")).get("repos", [])
    )


def _get_options() -> tuple[list[str], list[str], ChainMap[str, str]]:
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__, allow_abbrev=False)

    _ = parser.add_argument(
        "--gh-map-config",
        dest="config",
        default=".gh-map.toml",
        type=Path,
        help="""
        Config file containing repos = ['user/repo'] items.
        """,
    )
    _ = parser.add_argument(
        "--gh-map-repo",
        dest="repos",
        action="append",
        default=[],
        help="""
        Additional `user/repo` items.
        """,
    )
    _ = parser.add_argument(
        "args",
        nargs="*",
        default=["workflow", "run", "update-copier.yml"],
        help="Command to run with gh. [default: %(default)s]",
    )

    _ = parser.add_argument(
        "--gh-map-pager",
        dest="pager",
        default="cat",
        help="""
        Pager value.  Default is `cat`.
        """,
    )

    _ = parser.add_argument(
        "--gh-map-self",
        action="store_true",
        help="""
        Apply action to this repo
        """,
    )

    _ = parser.add_argument(
        "--automerge", action="store_true", help="Add option `-F automerge=true`"
    )

    options, extra_args = parser.parse_known_args()

    env = ChainMap({"GH_PAGER": options.pager}, os.environ)

    repos = [*options.repos, *_get_repos(options.config)]

    if options.gh_map_self:
        repos.insert(
            0,
            subprocess
            .check_output(["gh", "repo", "set-default", "--view"])
            .decode("utf-8")
            .strip(),
        )

    args = [
        *options.args,
        *extra_args,
        *(["-F", "automerge=true"] if options.automerge else []),
    ]

    return repos, args, env


def _main() -> bool:
    repos, args, env = _get_options()

    failure = False
    for repo in repos:
        cmd = ["gh", *args, "--repo", repo]
        print(shlex.join(cmd))
        failure = bool(subprocess.call(cmd, env=env)) or failure
    return failure


if __name__ == "__main__":
    raise SystemExit(_main())
