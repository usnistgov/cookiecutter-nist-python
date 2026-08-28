"""Post generate hooks."""

from __future__ import annotations

from pathlib import Path


def remove_update_copier() -> None:
    """Remove unused update-copier.yml file."""
    path = Path(".github/workflows/update-copier.yml")
    path.unlink(missing_ok=True)


def remove_ruff_toml() -> None:
    """Remove unused ruff.toml file"""
    Path("ruff.toml").unlink(missing_ok=True)


if __name__ == "__main__":
    remove_update_copier()
    remove_ruff_toml()
