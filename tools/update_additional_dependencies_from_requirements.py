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
    from collections.abc import Sequence


SUPPORTED_FROM_ID = frozenset(("rust-just", "typos", "codespell", "ruff-format"))

_ARGUMENT_HELP_TEMPLATE = (
    "The `{}` argument to the YAML dumper. "
    "See https://yaml.readthedocs.io/en/latest/detail/"
    "#indentation-of-block-sequences"
)


def _get_versions_from_ids(loaded: dict[str, Any]) -> dict[str, Any]:
    versions = {}
    for repo in loaded["repos"]:
        if repo["repo"] not in {"local", "meta"}:
            for hook in repo["hooks"]:
                if (hid := hook["id"]) in SUPPORTED_FROM_ID:
                    # `mirrors-mypy` uses versions with a 'v' prefix, so we
                    # have to strip it out to get the mypy version.
                    cleaned_rev = repo["rev"].removeprefix("v")
                    versions[hid] = cleaned_rev

    # add ruff key
    versions["ruff"] = versions["ruff-format"]
    return versions


def _get_versions_from_requirements(
    requirements_path: Path | None, dependencies: Sequence[str]
) -> dict[str, Any]:
    if requirements_path is None:
        if dependencies:
            msg = "have dependencies without a requirements_path file"
            raise ValueError(msg)
        return {}

    from requirements import parse

    versions = {}
    with requirements_path.open(encoding="utf-8") as f:
        for requirement in parse(f):
            if requirement.name in dependencies:
                versions[requirement.name] = requirement.specs[0][-1]
    return versions


def main(argv: Sequence[str] | None = None) -> int:
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
        "-r",
        "--requirements",
        type=Path,
        help="Requirements file to lookup pinned requirements.",
    )
    parser.add_argument(
        "-d",
        "--dep",
        dest="dependencies",
        type=str,
        help="Dependency to lookup in requirements file.  Can specify multiple times",
        action="append",
        default=[],
    )

    args = parser.parse_args(argv)
    path: Path = args.path
    yaml_mapping: int = args.yaml_mapping
    yaml_sequence: int = args.yaml_sequence
    yaml_offset: int = args.yaml_offset

    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    yaml.indent(yaml_mapping, yaml_sequence, yaml_offset)

    with path.open(encoding="utf-8") as f:
        loaded = yaml.load(f)

    versions = _get_versions_from_ids(loaded)
    versions.update(
        _get_versions_from_requirements(args.requirements, args.dependencies)
    )

    updated = []
    for repo in loaded["repos"]:
        for hook in repo["hooks"]:
            for i, dep in enumerate(hook.get("additional_dependencies", ())):
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
