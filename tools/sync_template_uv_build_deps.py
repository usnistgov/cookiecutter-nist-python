"""
Script to update template uv-build version pin

NOTE: use re.sub here to work with template pyproject.toml
"""
# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false

# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "packaging>=26.0",
#     "ruamel-yaml>=0.19.1",
# ]
# ///
from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, cast

from packaging.version import Version
from ruamel.yaml import (  # type: ignore[import-not-found]  # pyrefly: ignore[missing-import]  # ty: ignore[unresolved-import]
    YAML,
)

if TYPE_CHECKING:
    from typing import Any


def _get_uv_version(pre_commit_config: Path) -> Version:
    yaml = YAML()  # pright: ignore[reportUnknownVariableType]
    loaded = cast("dict[str, Any]", yaml.load(pre_commit_config))
    for repo in loaded["repos"]:
        if repo["repo"].endswith("uv-pre-commit"):
            return Version(repo["rev"])

    msg = "No repo found for uv"
    raise ValueError(msg)


def _get_uv_build_dep(uv_version: Version) -> str:
    release = list(uv_version.release)
    release[1] += 1
    release[2] = 0

    version_upper = ".".join(str(x) for x in release)
    return f"uv-build>={uv_version},<{version_upper}"


def _update_pyproject(pyproject: Path, uv_build_dep: str) -> int:

    out = re.sub(
        r"uv-build>=\d+\.\d+\.\d+,<\d+\.\d+\.\d+",
        uv_build_dep,
        pyproject.read_text(encoding="utf-8"),
    )

    _ = pyproject.write_text(out, encoding="utf-8")
    return 0


def main() -> int:
    """Main function."""
    template = Path("{{cookiecutter.project_name}}")

    pyproject = template / "pyproject.toml"
    pre_commit = template / ".pre-commit-config.yaml"

    uv_build_dep = _get_uv_build_dep(_get_uv_version(pre_commit))

    print("uv_build_dep", uv_build_dep)  # noqa: T201

    return _update_pyproject(pyproject, _get_uv_build_dep(_get_uv_version(pre_commit)))


if __name__ == "__main__":
    raise SystemExit(main())
