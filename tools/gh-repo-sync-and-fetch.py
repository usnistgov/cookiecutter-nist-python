"""sync and fetch multiple local repos"""
# /// script
# requires-python = ">=3.12"
# ///
# ruff:file-ignore[invalid-module-name]

from __future__ import annotations

import logging
import shlex
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

FORMAT = "[%(name)s - %(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger("sync-pyproject-min-versions")

root = Path(__file__).parent.parent.parent


def _get_remote_mapping(path: Path) -> list[dict[str, Any]]:
    import tomllib

    config = tomllib.loads(path.read_text(encoding="utf-8")).get("sync-and-fetch", {})

    defaults = config.get("defaults", {})
    defaults.setdefault("path", "..")
    defaults.setdefault("remote", "origin")

    out: list[dict[str, Any]] = []
    for repo in config.get("repos", []):
        if isinstance(repo, str):
            out.append({"repo": repo, **defaults})
        elif isinstance(repo, dict):
            out.append({**defaults, **repo})
        else:
            msg = f"Unknown type {type(repo)} in sync-and-fetch.repos"
            raise TypeError(msg)

    return out


def _call(args: list[str], cwd: Path, ntry: int = 3) -> int:
    logger.info("Run: %s", shlex.join(args))
    logger.info("cwd: %s", cwd)
    for i in range(ntry):
        logger.info("try: %s", i + 1)
        code = subprocess.run(
            args,
            cwd=cwd,
            check=False,
        ).returncode

        if not code:
            return code
    return 1


def main() -> bool:
    """Main functionality"""
    mapping = _get_remote_mapping(Path("./.gh-map.toml"))
    code = 0

    for d in mapping:
        path = Path(d["path"]).expanduser() / d["repo"]
        if not path.exists():
            msg = f"Path {path} does not exist"
            raise ValueError(msg)
        code += _call(["gh", "repo", "sync"], cwd=path)
        code += _call(["git", "fetch", "--prune", d["remote"]], cwd=path)
    return bool(code)


if __name__ == "__main__":
    raise SystemExit(main())
