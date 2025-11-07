"""Process justfile formatting"""

import sys
from argparse import ArgumentParser
from pathlib import Path


def _format_file(path: Path) -> None:
    from subprocess import check_call

    check_call(
        [
            "just",
            "--fmt",
            "--unstable",
            "--justfile",
            str(path),
        ]
    )


def _main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "paths",
        type=Path,
        nargs="+",
    )

    options = parser.parse_args()

    for path in options.paths:
        _format_file(path)


if __name__ == "__main__":
    sys.exit(_main())
