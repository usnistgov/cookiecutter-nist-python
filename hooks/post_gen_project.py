#!/usr/bin/env python
from pathlib import Path

PROJECT_PATH = Path.cwd()


if __name__ == "__main__":
    if "no" in "{{ cookiecutter.command_line_interface|lower }}":
        cli_path = PROJECT_PATH / "src" / "{{ cookiecutter.project_slug }}" / "cli.py"
        cli_path.unlink()
