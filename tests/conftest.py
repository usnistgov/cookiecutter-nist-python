"""Utilities to build examples"""

from __future__ import annotations

import os
import logging

import shutil
from pathlib import Path
from typing import Any

import pytest

from utils import run_inside_dir

# from itertools import product


# * Examples setup ---------------------------------------------------------------------
ROOT = (Path(__file__).parent / "..").resolve()
OUTPUT_PATH = ROOT / "cached_examples"


# SPHINX_THEMES = ["furo", "book"]
# COMMAND_LINE_INTERFACE = ["nocli", "click", "typer"]
# SPHINX_THEMES_AND_CLI = product(SPHINX_THEMES, COMMAND_LINE_INTERFACE)

SPHINX_THEMES_AND_CLI = [
    ("book", "nocli"),
    ("book", "typer"),
    ("book", "click"),
    ("furo", "typer"),
]

MARKER_MAP = {
    "furo": "furo",
    "book": "sphinx_book_theme",
    "nocli": "No command-line interface",
    "click": "Click",
    "typer": "Typer",
}

PARAMS: list[Any] = []
for style in ["cookie", "copier"]:
    for theme, cli in SPHINX_THEMES_AND_CLI:
        sphinx_theme, command_line_interface = [MARKER_MAP[k] for k in (theme, cli)]

        def _update_project_name(d):
            if style != "cookie":
                d["project_name"] = f"{style}-" + d["project_name"]
            return d

        d = _update_project_name(
            {
                "project_name": f"testpackage-{theme}-{cli}",
                "style": style,
                "extra_context": {
                    "sphinx_theme": sphinx_theme,
                    "command_line_interface": command_line_interface,
                },
            }
        )

        marks = [getattr(pytest.mark, k) for k in (theme, cli, style)]
        if theme == "book" and cli == "nocli":
            # add in default
            PARAMS.append(pytest.param(d, marks=marks + [pytest.mark.default]))

            # add in longname
            d = _update_project_name(
                dict(d, project_name=f"a-super-long-package-name-{theme}-{cli}")
            )
            PARAMS.append(pytest.param(d, marks=marks + [pytest.mark.longname]))

        else:
            PARAMS.append(pytest.param(d, marks=marks))


# * nox options ------------------------------------------------------------------------
def pytest_addoption(parser):
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
def nox_opts(pytestconfig):
    return pytestconfig.getoption("nox_opts")


@pytest.fixture(scope="session")
def nox_session_opts(pytestconfig):
    return pytestconfig.getoption("nox_session_opts")


# * Fixtures ---------------------------------------------------------------------------
@pytest.fixture(
    scope="session",
    params=PARAMS,
)
def example_path(request):
    project_name = request.param["project_name"]
    extra_context = request.param["extra_context"]
    style = request.param["style"]

    path = _create_example(
        project_name=project_name, extra_context=extra_context, style=style
    )

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
def pytest_collection_modifyitems(config, items):
    for item in items:
        marker = item.originalname.split("_")[-1]
        item.add_marker(getattr(pytest.mark, marker))

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

    logging.info(f"cleaning {directory_path}")
    if not directory_path.exists():
        return

    if keep is None:
        keep = [".nox"]
    elif isinstance(keep, str):
        keep = [keep]

    for p in directory_path.glob("*"):
        x = p.name
        if x in keep:
            logging.debug(f"skipping {p}")
        elif p.is_dir():
            logging.debug(f"removing directory {p}")
            shutil.rmtree(p)
        else:
            logging.debug(f"removing file {p}")
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

    if extra_context is None:
        extra_context = {}
    else:
        extra_context = extra_context.copy()

    extra_context["project_name"] = project_name

    logging.info(f"baking in {output_dir}")
    logging.info(f"project_name: {project_name}")
    logging.info(f"extra_context: {extra_context}")
    logging.info(f"style: {style}")

    if style == "cookie":
        from cookiecutter.main import cookiecutter

        cookiecutter(
            template=str(template),
            output_dir=str(output_dir),
            no_input=no_input,
            extra_context=extra_context,
            overwrite_if_exists=overwrite_if_exists,
            **kws,
        )

    elif style == "copier":
        import copier

        copier.run_copy(
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

    run_inside_dir(f"nox -s requirements", rendered_dir)

    # if have userconfig, copy it:
    config = ROOT / "config" / "userconfig.toml"

    if config.exists():
        shutil.copy(str(config), str(rendered_dir / "config"))

    # git init?
    if not (rendered_dir / ".git").exists():
        run_inside_dir("git init", rendered_dir)
    run_inside_dir("git add .", rendered_dir)
