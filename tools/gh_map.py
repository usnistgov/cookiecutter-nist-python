"""Run workflow over multiple repos."""
# /// script
# requires-python = ">=3.12"
# ///

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
    "wpk-nist-gov/just-pre-commit",
]


def _get_options() -> list[str]:
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__, allow_abbrev=False)

    _ = parser.add_argument(
        "args",
        nargs="*",
        default=["workflow", "run", "update-copier.yml"],
        help="Command to run with gh. [default: %(default)s]",
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


def _main() -> bool:
    args = _get_options()

    from subprocess import call

    failure = False
    for repo in REPOS:
        cmd = ["gh", *args, "--repo", repo]
        print(shlex.join(cmd))
        failure = bool(call(cmd)) or failure
    return failure


if __name__ == "__main__":
    raise SystemExit(_main())
