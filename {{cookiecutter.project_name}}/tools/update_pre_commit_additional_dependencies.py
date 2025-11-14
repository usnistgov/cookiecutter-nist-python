"""Update ``additional_dependencies`` in ``.pre-commit-config.yaml``"""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "ruamel.yaml",
#     "requirements-parser",
# ]
# ///
# NOTE: adapted from https://github.com/pre-commit/sync-pre-commit-deps
# ruff: noqa: D103, T201
from __future__ import annotations

import argparse
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

import ruamel.yaml

if TYPE_CHECKING:
    from collections.abc import Container, Sequence


SUPPORTED_FROM_ID = ["typos", "codespell", "ruff-format"]
SUPPORT_TO_ID = ["doccmd", "justfile-format", "nbqa"]

_ARGUMENT_HELP_TEMPLATE = (
    "The `{}` argument to the YAML dumper. "
    "See https://yaml.readthedocs.io/en/latest/detail/"
    "#indentation-of-block-sequences"
)


def _get_versions_from_ids(
    loaded: dict[str, Any],
    hook_ids_from: Container[str],
) -> dict[str, Any]:
    versions = {}
    for repo in loaded["repos"]:
        if repo["repo"] not in {"local", "meta"}:
            for hook in repo["hooks"]:
                hid = hook["id"]
                if hid in hook_ids_from:
                    # `mirrors-mypy` uses versions with a 'v' prefix, so we
                    # have to strip it out to get the mypy version.
                    cleaned_rev = repo["rev"].removeprefix("v")
                    versions[hid] = cleaned_rev

    # add ruff key
    versions["ruff"] = versions["ruff-format"]
    return versions


@lru_cache
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


@lru_cache
def _get_version_from_lastversion(dep: str) -> str:
    from lastversion import latest

    return latest(dep, output_format="tag")


def _get_versions_from_lastversion(dependencies: Sequence[str]) -> dict[str, Any]:
    return {dep: _get_version_from_lastversion(dep) for dep in dependencies}


def _get_hook_ids(loaded: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for repo in loaded["repos"]:
        if repo["repo"] not in {"local", "meta"}:
            out.extend(hook["id"] for hook in repo["hooks"])
    return out


def _limit_hooks(
    hook_ids: Sequence[str],
    use_all: bool,
    include: Sequence[str],
    exclude: Sequence[str],
) -> list[str]:
    include = hook_ids if use_all else include
    return [x for x in include if x not in exclude]


def _process_file(
    path: Path,
    yaml_mapping: int,
    yaml_sequence: int,
    yaml_offset: int,
    to_all: bool,
    to_include: Sequence[str],
    to_exclude: Sequence[str],
    from_all: bool,
    from_include: Sequence[str],
    from_exclude: Sequence[str],
    requirements: Path | None,
    lastversion_dependencies: Sequence[str],
) -> int:
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    yaml.indent(yaml_mapping, yaml_sequence, yaml_offset)

    with path.open(encoding="utf-8") as f:
        loaded = yaml.load(f)

    hook_ids = _get_hook_ids(loaded)
    hook_ids_update = _limit_hooks(
        hook_ids, use_all=to_all, include=to_include, exclude=to_exclude
    )
    hook_ids_from = _limit_hooks(
        hook_ids, use_all=from_all, include=from_include, exclude=from_exclude
    )

    versions = _get_versions_from_ids(loaded, hook_ids_from)
    versions.update(_get_versions_from_requirements(requirements))
    versions.update(_get_versions_from_lastversion(lastversion_dependencies))

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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        type=Path,
        nargs="*",
        help="The pre-commit config file to sync to.",
    )

    # yaml defaults are my preference
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
    # hook id to extract from
    parser.add_argument(
        "--from",
        dest="from_include",
        action="append",
        default=SUPPORTED_FROM_ID,
        help=f"hook id's to extract requirements from.  Defaults to {SUPPORTED_FROM_ID}",
    )
    parser.add_argument(
        "--from-all",
        action="store_true",
        help="Extract dependencies from all hook id's",
    )
    parser.add_argument(
        "--from-exclude",
        action="append",
        default=[],
        help="Hook id's to exclude extracting from. Note that this is applied even if pass ``--from-all``",
    )
    # hook id's to update
    parser.add_argument(
        "--to",
        dest="to_include",
        action="append",
        default=SUPPORT_TO_ID,
        help=f"hook id's to allow update of additional_dependencies.  Defaults to {SUPPORT_TO_ID}",
    )
    parser.add_argument(
        "--to-all",
        action="store_true",
        help="Update dependencies of all hooks",
    )
    parser.add_argument(
        "--to-exclude",
        action="append",
        default=[],
        help="Hook id's to exclude updating.  Note that this is applied even if pass ``--to-all``",
    )
    parser.add_argument(
        "-r",
        "--requirements",
        type=Path,
        default=None,
        help="Requirements file to lookup pinned requirements to update.",
    )
    # use lastversion?
    parser.add_argument(
        "-l",
        "--last",
        dest="lastversion_dependencies",
        type=str,
        help="Dependency to lookup using `lastversion`.  Requires network access and `lastversion` to be installed.",
        action="append",
        default=[],
    )

    args = parser.parse_args(argv)
    paths: list[Path] = args.paths or [Path(".pre-commit-config.yaml")]

    out = 0
    for path in paths:
        out += _process_file(
            path,
            yaml_mapping=args.yaml_mapping,
            yaml_sequence=args.yaml_sequence,
            yaml_offset=args.yaml_offset,
            to_all=args.to_all,
            to_include=args.to_include,
            to_exclude=args.to_exclude,
            from_all=args.from_all,
            from_include=args.from_include,
            from_exclude=args.from_exclude,
            requirements=args.requirements,
            lastversion_dependencies=args.lastversion_dependencies,
        )

    return out


if __name__ == "__main__":
    raise SystemExit(main())
