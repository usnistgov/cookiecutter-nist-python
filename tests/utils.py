from __future__ import annotations

import os
import shlex
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def inside_dir(dirpath: str | Path) -> Iterator[None]:
    """
    Execute code from inside the given directory
    :param dirpath: String, path of the directory the command is being run.
    """
    old_path = Path.cwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


def run_inside_dir(command: str, dirpath: str | Path) -> int:
    """Run a command from inside a given directory, returning the exit status"""
    with inside_dir(dirpath):
        return subprocess.check_call(shlex.split(command))
