# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "ruamel.yaml",
#     "lastversion",
# ]
# ///
# NOTE: adapted from https://github.com/pre-commit/sync-pre-commit-deps
# ruff: noqa: C901, D100, D103, T201, PLR0914, PLR0912
from __future__ import annotations

import argparse
import pathlib
from typing import TYPE_CHECKING

import ruamel.yaml

if TYPE_CHECKING:
    from collections.abc import Sequence


SUPPORTED = frozenset(("rust-just", "typos", "codespell", "ruff-format"))

_ARGUMENT_HELP_TEMPLATE = (
    "The `{}` argument to the YAML dumper. "
    "See https://yaml.readthedocs.io/en/latest/detail/"
    "#indentation-of-block-sequences"
)


def _get_lastversion(package: str) -> str:
    from lastversion import latest

    return latest(package, output_format="tag")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename",
        default=".pre-commit-config.yaml",
        help="The pre-commit config file to sync to.",
    )

    # defaults below match pre-commit config as documented
    parser.add_argument(
        "--yaml-mapping",
        type=int,
        default=4,
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
        "--lastversion",
        action="store_true",
    )

    args = parser.parse_args(argv)
    filename: str = args.filename
    yaml_mapping: int = args.yaml_mapping
    yaml_sequence: int = args.yaml_sequence
    yaml_offset: int = args.yaml_offset
    use_lastversion: bool = args.lastversion

    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    yaml.indent(yaml_mapping, yaml_sequence, yaml_offset)

    with pathlib.Path(filename).open(encoding="utf-8") as f:
        loaded = yaml.load(f)

    versions = {}
    for repo in loaded["repos"]:
        if repo["repo"] not in {"local", "meta"}:
            for hook in repo["hooks"]:
                if (hid := hook["id"]) in SUPPORTED:
                    # `mirrors-mypy` uses versions with a 'v' prefix, so we
                    # have to strip it out to get the mypy version.
                    cleaned_rev = repo["rev"].removeprefix("v")
                    versions[hid] = cleaned_rev

    # add ruff key
    versions["ruff"] = versions["ruff-format"]

    # update other versions
    if use_lastversion:
        for hid in SUPPORTED:
            if hid not in versions:
                versions[hid] = _get_lastversion(hid)

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
        print(f"Writing updates to {filename}:")
        for hid, name in updated:
            print(f"\tSetting {hid!r} dependency {name!r} to {versions[name]}")

        with pathlib.Path(filename).open("w+", encoding="utf-8") as f:
            yaml.dump(loaded, f)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
