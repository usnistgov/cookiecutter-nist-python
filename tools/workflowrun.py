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


def _get_options() -> tuple[str, list[str]]:
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)

    _ = parser.add_argument(
        "-w",
        "--workflow",
        default="update-copier.yml",
        help="workflow file name.  [default %(default)s]",
    )
    _ = parser.add_argument(
        "--automerge", action="store_true", help="Add option `-F automerge=true`"
    )

    options, extra_args = parser.parse_known_args()

    workflow = options.workflow

    args = [*(["-F", "automerge=true"] if options.automerge else []), *extra_args]

    return workflow, args


def _main() -> int:
    workflow, args = _get_options()

    print("workflow:", workflow)
    print("args:", args)

    from subprocess import call

    out = 0
    for repo in REPOS:
        cmd = ["gh", "workflow", "run", workflow, "--repo", repo, *args]
        print(shlex.join(cmd))
        out += call(cmd)
    return out


if __name__ == "__main__":
    raise SystemExit(_main())
