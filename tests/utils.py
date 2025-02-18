from __future__ import annotations

import logging
import os
import shlex
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

logger = logging.getLogger(__name__)


@contextmanager
def inside_dir(dirpath: str | Path) -> Iterator[None]:
    """
    Execute code from inside the given directory
    :param dirpath: String, path of the directory the command is being run.
    """
    old_path = Path.cwd()
    try:  # pylint: disable=too-many-try-statements
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


def run_inside_dir(
    command: str, dirpath: str | Path, env: dict[str, str] | None = None
) -> int:
    """Run a command from inside a given directory, returning the exit status"""

    if env is not None:
        env = {**os.environ, **env}

    with inside_dir(dirpath):
        logger.info("Run: %s", command)
        return subprocess.check_call(shlex.split(command), env=env)
