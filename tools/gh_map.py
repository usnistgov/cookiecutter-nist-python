"""Run workflow over multiple repos."""

# ruff: noqa: T201
from __future__ import annotations

import shlex

REPOS = [
    "usnistgov/cmomy",
    "usnistgov/tmmc-lnpy",
    "usnistgov/thermoextrap",
    "usnistgov/module-utilities",
    "usnistgov/pyproject2conda",
    "usnistgov/analphipy",
    "usnistgov/open-notebook",
    "usnistgov/uv-workon",
    "wpk-nist-gov/sync-pre-commit-hooks",
    "wpk-nist-gov/typecheck-runner",
]


def _get_options() -> list[str]:
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)

    _ = parser.add_argument(
        "args",
        nargs="*",
        default=["workflow", "run", "update-copier.yml"],
        help="Command to run with gh. [default %(default)s]",
    )

    _ = parser.add_argument(
        "--automerge", action="store_true", help="Add option `-F automerge=true`"
    )

    options, extra_args = parser.parse_known_args()

    return [
        *options.args,
        *extra_args,
        *(["-F", "automerge=true"] if options.automerge else []),
    ]


def _main() -> int:
    args = _get_options()

    from subprocess import call

    out = 0
    for repo in REPOS:
        cmd = ["gh", *args, "--repo", repo]
        print(shlex.join(cmd))
        out += call(cmd)
    return out


if __name__ == "__main__":
    raise SystemExit(_main())
