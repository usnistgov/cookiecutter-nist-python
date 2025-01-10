"""Utilities to build examples"""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import Any, Iterator

import pytest

from .utils import run_inside_dir

# * Examples setup ---------------------------------------------------------------------
ROOT = (Path(__file__).parent / "..").resolve()
OUTPUT_PATH = ROOT / "cached_examples"


SPHINX_THEMES_AND_CLI = [
    ("book", "nocli"),
    ("book", "typer"),
    ("book", "click"),
    ("furo", "typer"),
]

MARKER_MAP = {
    "furo": "furo",
    "book": "sphinx_book_theme",
    "nocli": "none",
    "click": "click",
    "typer": "typer",
}

PARAMS: list[Any] = []
for style in ["cookie", "copier"]:
    for theme, cli in SPHINX_THEMES_AND_CLI:
        sphinx_theme, command_line_interface = (MARKER_MAP[k] for k in (theme, cli))

        def _update_project_name(d: dict[str, Any], style: str) -> dict[str, Any]:
            if style != "cookie":
                d["project_name"] += f"-{style}"
            return d

        d = _update_project_name(
            {
                "project_name": f"testpackage-{theme}-{cli}",
                "style": style,
                "extra_context": {
                    "sphinx_theme": sphinx_theme,
                    "command_line_interface": command_line_interface,
                },
            },
            style=style,
        )

        marks = [getattr(pytest.mark, k) for k in (theme, cli, style)]
        if theme == "book" and cli == "nocli":
            # add in default
            PARAMS.append(pytest.param(d, marks=[*marks, pytest.mark.default]))

            # add in longname
            d = _update_project_name(
                dict(d, project_name=d["project_name"] + "-long-package-name"),
                style=style,
            )
            PARAMS.append(pytest.param(d, marks=[*marks, pytest.mark.longname]))

        else:
            PARAMS.append(pytest.param(d, marks=marks))


# * nox options ------------------------------------------------------------------------
def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--nox-opts",
        action="store",
        default="",
        help="options to be passed to nox",
    )

    parser.addoption(
        """--nox-session-opts""",
        action="store",
        default="",
        help="option to pass to nox (after --)",
    )

    parser.addoption(
        "--enable",
        action="store_true",
        default=False,
        help="enable some tests turned off by default",
    )


@pytest.fixture(scope="session")
def nox_opts(pytestconfig: pytest.Config) -> str:
    return pytestconfig.getoption("nox_opts")  # type: ignore[no-any-return]


@pytest.fixture(scope="session")
def nox_session_opts(pytestconfig: pytest.Config) -> str:
    return pytestconfig.getoption("nox_session_opts")  # type: ignore[no-any-return]


# * Fixtures ---------------------------------------------------------------------------
@pytest.fixture(
    scope="session",
    params=PARAMS,
)
def example_path(
    request: pytest.FixtureRequest, nox_opts: str, nox_session_opts: str
) -> Iterator[Path]:
    project_name = request.param["project_name"]
    extra_context = request.param["extra_context"]
    style = request.param["style"]

    path = _create_example(
        project_name=project_name, extra_context=extra_context, style=style
    )

    # add files to git
    if not (path / ".git").exists():
        run_inside_dir("git init", path)
    run_inside_dir("git add .", path)

    run_inside_dir(f"nox -s requirements {nox_opts} -- {nox_session_opts}", str(path))
    run_inside_dir("uv lock", str(path), env={"VIRTUAL_ENV": str(path / ".venv")})

    run_inside_dir("git add .", path)

    # change to example_path
    old_cwd = Path.cwd()
    os.chdir(path)
    yield path
    # Cleanup?
    os.chdir(old_cwd)


def _create_example(
    project_name: str, style: str, extra_context: dict[str, Any]
) -> Path:
    path = OUTPUT_PATH / project_name

    _clean_directory(path)
    _bake_project(project_name=project_name, style=style, extra_context=extra_context)

    return path


# * Automatic markers on tests ---------------------------------------------------------
def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    for item in items:
        marker = item.originalname.split("_")[-1]  # type: ignore[attr-defined]
        item.add_marker(getattr(pytest.mark, marker))  # pyright: ignore[reportUnknownArgumentType]

    if config.getoption("--enable"):
        # allow update version
        pass
    else:
        skip_disabled = pytest.mark.skip(reason="need --enable to run this test")
        for item in items:
            if "disable" in item.keywords:
                item.add_marker(skip_disabled)


# * Logging ----------------------------------------------------------------------------

FORMAT = "[%(name)s - %(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)


# * Utilities --------------------------------------------------------------------------
def _clean_directory(directory_path: Path, keep: str | list[str] | None = None) -> None:
    """Remove everything froma  directory path except those in `keep`"""

    logging.info("cleaning %s", directory_path)
    if not directory_path.exists():
        return

    if keep is None:
        keep = [".nox", ".venv", "uv.lock", "requirements"]
    elif isinstance(keep, str):
        keep = [keep]

    for p in directory_path.glob("*"):
        x = p.name
        if x in keep:
            logging.debug("skipping %s", p)
        elif p.is_dir():
            logging.debug("removing directory %s", p)
            shutil.rmtree(p)
        else:
            logging.debug("removing file %s", p)
            p.unlink()


def _bake_project(
    project_name: str,
    template: Path | None = None,
    output_dir: str | Path | None = None,
    no_input: bool = True,
    extra_context: dict[str, Any] | None = None,
    overwrite_if_exists: bool = True,
    style: str = "cookie",
    **kws: Any,
) -> None:
    """Bake a cookiecutter"""

    if template is None:
        template = ROOT
    if output_dir is None:
        output_dir = OUTPUT_PATH
    output_dir = Path(output_dir)

    extra_context = {} if extra_context is None else extra_context.copy()

    extra_context["project_name"] = project_name

    logging.info("baking in %s", output_dir)
    logging.info("project_name: %s", project_name)
    logging.info("extra_context: %s", extra_context)
    logging.info("style: %s", style)

    if style == "cookie":
        from cookiecutter.main import (  # pyright: ignore[reportMissingTypeStubs]
            cookiecutter,  # pyright: ignore[reportUnknownVariableType]
        )

        cookiecutter(
            template=str(template),
            output_dir=str(output_dir),
            no_input=no_input,
            extra_context=extra_context,
            overwrite_if_exists=overwrite_if_exists,
            **kws,
        )

    elif style == "copier":
        import copier  # pyright: ignore[reportMissingImports]

        copier.run_copy(  # pyright: ignore[reportUnknownMemberType]
            src_path=str(template),
            dst_path=str(output_dir / project_name),
            data=extra_context,
            vcs_ref="HEAD",
            unsafe=True,
            defaults=True,
        )

    # create .nox if doesn't exist
    rendered_dir = Path(output_dir) / project_name
    (rendered_dir / ".nox").mkdir(exist_ok=True)
