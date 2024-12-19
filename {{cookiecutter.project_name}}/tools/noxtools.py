"""Utilities to wonferrk with nox"""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import TYPE_CHECKING

from nox.logger import logger

if TYPE_CHECKING:
    import sys
    from collections.abc import Iterable, Iterator
    from typing import Any, Callable, Literal, Union

    from nox import Session

    PathLike = Union[str, Path]


# * Top level installation functions ---------------------------------------------------
def py_prefix(python_version: Any) -> str:
    """
    Get python prefix.

    `python="3.8` -> "py38"
    """
    if isinstance(python_version, str):
        return "py" + python_version.replace(".", "")
    msg = f"passed non-string value {python_version}"
    raise ValueError(msg)


def _verify_path(
    path: PathLike,
) -> Path:
    path = Path(path)
    if not path.is_file():
        msg = f"Path {path} is not a file"
        raise ValueError(msg)
    return path


def _verify_paths(
    paths: PathLike | Iterable[PathLike] | None,
) -> list[Path]:
    if paths is None:
        return []
    if isinstance(paths, (str, Path)):
        paths = [paths]
    return [_verify_path(p) for p in paths]


def infer_requirement_path_with_fallback(
    name: str | None,
    ext: str | None = None,
    python_version: str | None = None,
    lock: bool = False,
    check_exists: bool = True,
    lock_fallback: bool = False,
) -> tuple[bool, Path]:
    """Get the requirements file from options with fallback."""
    if lock_fallback:
        try:
            path = infer_requirement_path(
                name=name,
                ext=ext,
                python_version=python_version,
                lock=lock,
                check_exists=True,
            )
        except FileNotFoundError:
            logger.info("Falling back to non-locked")
            lock = False
            path = infer_requirement_path(
                name=name,
                ext=ext,
                python_version=python_version,
                lock=lock,
                check_exists=True,
            )

    else:
        path = infer_requirement_path(
            name=name,
            ext=ext,
            python_version=python_version,
            lock=lock,
            check_exists=check_exists,
        )
    return lock, path


def infer_requirement_path(
    name: str | None,
    ext: str | None = None,
    python_version: str | None = None,
    lock: bool = False,
    check_exists: bool = True,
) -> Path:
    """Get filename for a conda yaml or pip requirements file."""
    if name is None:
        msg = "must supply name"
        raise ValueError(msg)

    # adjust filename
    filename = name
    if ext is not None and not filename.endswith(ext):
        filename += ext
    if ext != ".txt" and python_version is not None:
        prefix = py_prefix(python_version)
        if not filename.startswith(prefix):
            filename = f"{prefix}-{filename}"

    if lock:
        if filename.endswith(".yaml"):
            filename = filename.rstrip(".yaml") + "-conda-lock.yml"
        elif filename.endswith(".yml"):
            filename = filename.rstrip(".yml") + "-conda-lock.yml"
        elif filename.endswith(".txt"):
            pass
        else:
            msg = f"unknown file extension for {filename}"
            raise ValueError(msg)

        filename = f"./requirements/lock/{filename}"
    else:
        filename = f"./requirements/{filename}"

    path = Path(filename)
    if check_exists and not path.is_file():
        msg = f"{path} does not exist"
        raise FileNotFoundError(msg)

    return path


def _infer_requirement_paths(
    names: str | Iterable[str] | None,
    lock: bool = False,
    ext: str | None = None,
    python_version: str | None = None,
) -> list[Path]:
    if names is None:
        return []

    if isinstance(names, str):
        names = [names]
    return [
        infer_requirement_path(
            name,
            lock=lock,
            ext=ext,
            python_version=python_version,
        )
        for name in names
    ]


def get_python_full_path(session: Session) -> str:
    """Full path to session python executable."""
    path = session.run_always(
        "python",
        "-c",
        "import sys; print(sys.executable)",
        silent=True,
    )
    if not isinstance(path, str):
        msg = "accessing python_full_path with value None"
        raise TypeError(msg)
    return path.strip()


# * Utilities --------------------------------------------------------------------------
def combine_list_str(opts: str | Iterable[str]) -> list[str]:
    """Cleanup str/list[str] to list[str]"""
    if not opts:
        return []

    if isinstance(opts, str):
        opts = [opts]
    return shlex.split(" ".join(opts))


def combine_list_list_str(opts: Iterable[str | Iterable[str]]) -> Iterable[list[str]]:
    """Cleanup Iterable[str/list[str]] to Iterable[list[str]]."""
    return (combine_list_str(opt) for opt in opts)


def open_webpage(path: str | Path | None = None, url: str | None = None) -> None:
    """
    Open webpage from path or url.

    Useful if want to view webpage with javascript, etc., as well as static html.
    """
    import webbrowser
    from urllib.request import pathname2url

    if path:
        url = "file://" + pathname2url(str(Path(path).absolute()))
    if url:
        webbrowser.open(url)


def session_run_commands(
    session: Session,
    commands: list[list[str]] | None,
    external: bool = True,
    **kws: Any,
) -> None:
    """Run commands command."""
    if commands:
        kws.update(external=external)
        for opt in combine_list_list_str(commands):
            session.run(*opt, **kws)
