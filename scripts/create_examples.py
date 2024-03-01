"""Script to create example files"""

from __future__ import annotations

import logging
import os
import shlex
import shutil
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

FORMAT = "%(message)s [%(name)s - %(levelname)s]"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)


ROOT = (Path(__file__).parent / "..").resolve()
OUTPUT_PATH = ROOT / "cached_examples"


def _project_name(name: str) -> str:
    return f"testpackage-{name}"


EXTRA_CONTEXTS: dict[str, dict[str, str]] = {
    "default": {},
    "furo": {"sphinx_theme": "furo", "command_line_interface": "Click"},
    "typer": {"command_line_interface": "Typer"},
}


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
        return subprocess.check_call(shlex.split(command))  # noqa: S603


def clean_directory(directory_path: Path, keep: str | list[str] | None = None) -> None:
    """Remove everything froma  directory path except those in `keep`"""
    if keep is None:
        keep = [".nox"]
    elif isinstance(keep, str):
        keep = [keep]

    for p in directory_path.glob("*"):
        x = p.name
        if x in keep:
            logging.info("skipping %s", p)
        elif p.is_dir():
            logging.info("removing directory %s", p)
            shutil.rmtree(p)
        else:
            logging.info("removing file %s", p)
            p.unlink()


def bake(
    name: str,
    template: Path | None = None,
    output_dir: str | Path | None = None,
    no_input: bool = True,
    extra_context: dict[str, Any] | None = None,
    overwrite_if_exists: bool = True,
    **kws: Any,
) -> None:
    """Bake a cookiecutter"""
    from cookiecutter.main import cookiecutter

    if template is None:
        template = ROOT
    if output_dir is None:
        output_dir = OUTPUT_PATH
    if extra_context is None:
        extra_context = {}

    extra_context.setdefault("project_name", _project_name(name))

    logging.info("baking %s", output_dir)
    cookiecutter(
        template=str(template),
        output_dir=str(output_dir),
        no_input=no_input,
        extra_context=extra_context,
        overwrite_if_exists=overwrite_if_exists,
        **kws,
    )

    # create .nox if doesn't exist
    rendered_dir = Path(output_dir) / _project_name(name)
    (rendered_dir / ".nox").mkdir(exist_ok=True)

    # git init?
    if not (rendered_dir / ".git").exists():
        run_inside_dir("git init", rendered_dir)
        run_inside_dir("git add .", rendered_dir)


def clean_directories(names: str | list[str]) -> None:
    """Clean out directory."""
    if isinstance(names, str):
        names = [names]

    logging.info("to clean %s", names)

    if "all" in names:
        for d in OUTPUT_PATH.iterdir():
            logging.info("cleaning directory %s", d)
            clean_directory(d)
    else:
        for name in names:
            clean_directory(OUTPUT_PATH / _project_name(name))


def remove_directories(names: str | list[str]) -> None:
    """Remove whole directories."""
    if isinstance(names, str):
        names = [names]

    logging.info("to remove %s", names)

    if "all" in names:
        for d in OUTPUT_PATH.iterdir():
            logging.info("removing directory %s", d)
            shutil.rmtree(d)
    else:
        for name in names:
            shutil.rmtree(OUTPUT_PATH / _project_name(name))


def create_directories(names: str | list[str]) -> None:
    """Create directories."""
    if isinstance(names, str):
        names = [names]

    if "all" in names:
        names = ["default", "furo", "typer"]

    logging.info("to create %s", names)
    for name in names:
        bake(name=name, extra_context=EXTRA_CONTEXTS[name])


def main() -> None:
    """Main runner."""
    import argparse

    choices = [*list(EXTRA_CONTEXTS.keys()), "all"]

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    commands = {
        k: subparsers.add_parser(k, help=f"{k} examples")
        for k in ("create", "clean", "recreate", "remove")
    }

    for v in commands.values():
        v.add_argument(
            "values",
            choices=choices,
            help="examples to apply to",
            nargs="*",
            default="all",
        )

    parsed = parser.parse_args()

    if parsed.command is None:
        parser.print_help()

    if parsed.command in {"clean", "recreate"}:
        clean_directories(parsed.values)
    if parsed.command in {"create", "recreate"}:
        create_directories(parsed.values)


if __name__ == "__main__":
    main()
