# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "ruamel.yaml",
#     "requirements-parser",
# ]
# ///
# NOTE: adapted from https://github.com/pre-commit/sync-pre-commit-deps
# ruff: noqa: D100, D103, T201
from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING, Any

import ruamel.yaml

if TYPE_CHECKING:
    from collections.abc import Container, Sequence


SUPPORTED_FROM_ID = ["typos", "codespell", "ruff-format"]
SUPPORT_TO_ID = ["doccmd", "justfile-format"]

_ARGUMENT_HELP_TEMPLATE = (
    "The `{}` argument to the YAML dumper. "
    "See https://yaml.readthedocs.io/en/latest/detail/"
    "#indentation-of-block-sequences"
)


def _get_versions_from_ids(
    loaded: dict[str, Any], hook_ids_from: Container[str]
) -> dict[str, Any]:
    versions = {}
    for repo in loaded["repos"]:
        if repo["repo"] not in {"local", "meta"}:
            for hook in repo["hooks"]:
                if (hid := hook["id"]) in hook_ids_from:
                    # `mirrors-mypy` uses versions with a 'v' prefix, so we
                    # have to strip it out to get the mypy version.
                    cleaned_rev = repo["rev"].removeprefix("v")
                    versions[hid] = cleaned_rev

    # add ruff key
    versions["ruff"] = versions["ruff-format"]
    return versions


def _get_versions_from_requirements(
    requirements_path: Path | None,
) -> dict[str, Any]:
    if requirements_path is None:
        return {}

    from requirements import parse

    versions = {}
    with requirements_path.open(encoding="utf-8") as f:
        for requirement in parse(f):
            versions[requirement.name] = requirement.specs[0][-1]
    return versions


def _get_versions_from_lastversion(dependencies: Sequence[str]) -> dict[str, Any]:
    if not dependencies:
        return {}

    from lastversion import latest

    versions = {}
    for dep in dependencies:
        versions[dep] = latest(dep, output_format="tag")
    return versions


def main(argv: Sequence[str] | None = None) -> int:  # noqa: PLR0914
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        default=".pre-commit-config.yaml",
        type=Path,
        nargs="?",
        help="The pre-commit config file to sync to.",
    )

    # defaults below match pre-commit config as documented
    parser.add_argument(
        "--yaml-mapping",
        type=int,
        default=2,
        help=_ARGUMENT_HELP_TEMPLATE.format("mapping"),
    )
    parser.add_argument(
        "--yaml-sequence",
        type=int,
        default=4,
        help=_ARGUMENT_HELP_TEMPLATE.format("sequence"),
    )
    parser.add_argument(
        "--yaml-offset",
        type=int,
        default=2,
        help=_ARGUMENT_HELP_TEMPLATE.format("offset"),
    )
    parser.add_argument(
        "--id",
        dest="hook_ids_update",
        type=str,
        help=f"hook id's to allow update of additional_dependencies.  Defaults to {SUPPORT_TO_ID}",
        action="append",
        default=SUPPORT_TO_ID,
    )
    parser.add_argument(
        "--from",
        dest="hook_ids_from",
        type=str,
        help=f"hook id's to extract requirements from.  Defaults to {SUPPORTED_FROM_ID}",
        action="append",
        default=SUPPORTED_FROM_ID,
    )
    parser.add_argument(
        "-l",
        "--last",
        dest="lastversion_dependencies",
        type=str,
        help="Dependency to lookup using `lastversion`.  Requires network access.",
        action="append",
        default=[],
    )
    parser.add_argument(
        "-r",
        "--requirements",
        type=Path,
        help="Requirements file to lookup pinned requirements.",
    )

    args = parser.parse_args(argv)
    path: Path = args.path

    yaml_mapping: int = args.yaml_mapping
    yaml_sequence: int = args.yaml_sequence
    yaml_offset: int = args.yaml_offset

    hook_ids_update: frozenset[str] = args.hook_ids_update
    hook_ids_from: frozenset[str] = args.hook_ids_from

    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    yaml.indent(yaml_mapping, yaml_sequence, yaml_offset)

    with path.open(encoding="utf-8") as f:
        loaded = yaml.load(f)

    versions = _get_versions_from_ids(loaded, hook_ids_from)
    versions.update(_get_versions_from_requirements(args.requirements))
    versions.update(_get_versions_from_lastversion(args.lastversion_dependencies))

    updated = []
    for repo in loaded["repos"]:
        for hook in repo["hooks"]:
            for i, dep in enumerate(hook.get("additional_dependencies", ())):
                if hook["id"] in hook_ids_update:
                    name, _, cur_version = dep.partition("==")
                    target_version = versions.get(name, cur_version)
                    if target_version != cur_version:
                        name_and_version = f"{name}=={target_version}"
                        hook["additional_dependencies"][i] = name_and_version
                        updated.append((hook["id"], name))

    if updated:
        print(f"Writing updates to {path}:")
        for hid, name in updated:
            print(f"\tSetting {hid!r} dependency {name!r} to {versions[name]}")

        with path.open("w+", encoding="utf-8") as f:
            yaml.dump(loaded, f)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
