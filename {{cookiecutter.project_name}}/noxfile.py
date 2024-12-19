"""Config file for nox."""

# * Imports ----------------------------------------------------------------------------
from __future__ import annotations

import shlex
import shutil
import sys
from functools import lru_cache, partial, wraps

from nox.virtualenv import CondaEnv

# Should only use on python version > 3.10
if sys.version_info < (3, 10):
    msg = "python>=3.10 required"
    raise RuntimeError(msg)

from dataclasses import dataclass
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Annotated,
    Literal,
    TypeAlias,
    TypedDict,
)

# fmt: off
sys.path.insert(0, ".")
from tools import uvxrun
from tools.dataclass_parser import DataclassParser, add_option, option
from tools.noxtools import (
    check_for_change_manager,
    combine_list_list_str,
    combine_list_str,
    get_python_full_path,
    infer_requirement_path,
    open_webpage,
    session_run_commands,
)

sys.path.pop(0)

# make sure these after
import nox  # type: ignore[unused-ignore,import]

# fmt: on

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator, Sequence

    from nox import Session


# * Names ------------------------------------------------------------------------------

PACKAGE_NAME = "{{ cookiecutter.project_name }}"
IMPORT_NAME = "{{ cookiecutter.project_slug }}"
KERNEL_BASE = "{{ cookiecutter.project_slug }}"

# * nox options ------------------------------------------------------------------------

ROOT = Path(__file__).parent

nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["test"]
nox.options.default_venv_backend = "uv"

# * Options ---------------------------------------------------------------------------

LOCK = True

PYTHON_ALL_VERSIONS = [
    c.split()[-1]
    for c in nox.project.load_toml("pyproject.toml")["project"]["classifiers"]
    if c.startswith("Programming Language :: Python :: 3.")
]
PYTHON_DEFAULT_VERSION = Path(".python-version").read_text(encoding="utf-8").strip()

UVXRUN_LOCK_REQUIREMENTS = "requirements/lock/py{}-uvxrun-tools.txt".format(
    PYTHON_DEFAULT_VERSION.replace(".", "")
)
UVXRUN_MIN_REQUIREMENTS = "requirements/uvxrun-tools.txt"


@lru_cache
def get_uvxrun_specs(requirements: str | None = None) -> uvxrun.Specifications:
    """Get specs for uvxrun."""
    requirements = requirements or UVXRUN_MIN_REQUIREMENTS
    if not Path(requirements).exists():
        requirements = None
    return uvxrun.Specifications.from_requirements(requirements=requirements)


class SessionOptionsDict(TypedDict, total=False):
    """Dict for options to nox.session"""

    python: str | list[str]
    venv_backend: str | Callable[..., CondaEnv]


CONDA_DEFAULT_KWS: SessionOptionsDict = {
    "python": PYTHON_DEFAULT_VERSION,
    "venv_backend": "micromamba|mamba|conda",
}
CONDA_ALL_KWS: SessionOptionsDict = {
    "python": PYTHON_ALL_VERSIONS,
    "venv_backend": "micromamba|mamba|conda",
}

DEFAULT_KWS: SessionOptionsDict = {"python": PYTHON_DEFAULT_VERSION}
ALL_KWS: SessionOptionsDict = {"python": PYTHON_ALL_VERSIONS}


# * Session command line options -------------------------------------------------------

OPT_TYPE: TypeAlias = list[str] | None
RUN_TYPE: TypeAlias = list[list[str]] | None

RUN_ANNO = Annotated[
    RUN_TYPE,
    option(
        help="Run external commands in session.  Specify multiple times for multiple commands.",
    ),
]
OPT_ANNO = Annotated[OPT_TYPE, option(help="Options to command.")]


@dataclass
class SessionParams(DataclassParser):
    """Holds all cli options"""

    # common parameters
    lock: bool = False
    update: bool = add_option("--update", "-U", help="update dependencies/package")
    version: str | None = None
    prune: bool = add_option(default=False, help="Pass `--prune` to conda env update")

    # requirements
    requirements_force: bool = False
    requirements_no_notify: bool = add_option(
        default=False,
        help="Skip notification of lock-compile",
    )

    # lock
    lock_force: bool = False
    lock_upgrade: bool = add_option(
        "--lock-upgrade",
        "-L",
        help="Upgrade all packages in lock files",
        default=False,
    )

    # test
    test_no_pytest: bool = False
    test_opts: OPT_TYPE = add_option(help="Options to pytest")
    test_run: RUN_ANNO = None
    no_cov: bool = False

    # coverage
    coverage: list[Literal["erase", "combine", "report", "html", "open"]] | None = None

    # testdist
    testdist_run: RUN_ANNO = None

    # docs
    docs: (
        list[
            Literal[
                "html",
                "build",
                "symlink",
                "clean",
                "livehtml",
                "linkcheck",
                "spelling",
                "showlinks",
                "open",
                "serve",
            ]
        ]
        | None
    ) = add_option("--docs", "-d", help="doc commands")
    docs_run: RUN_ANNO = None

    # typing
    typing: list[
        Literal[
            "clean",
            "mypy",
            "pyright",
            "pytype",
            "all",
            "mypy-notebook",
            "pyright-notebook",
            "typecheck-notebook",
        ]
    ] = add_option("--typing", "-m")
    typing_run: RUN_ANNO = None
    typing_run_internal: RUN_TYPE = add_option(
        help="Run internal (in session) commands.",
    )

    # build
    build: list[Literal["build", "version"]] | None = None
    build_run: RUN_ANNO = None
    build_isolation: bool = False
    build_outdir: str = "./dist"
    build_opts: OPT_ANNO = None
    build_silent: bool = False

    # publish
    publish: list[Literal["release", "test", "check"]] | None = add_option(
        "-p", "--publish"
    )

    # conda-recipe/grayskull
    conda_recipe: list[Literal["recipe", "recipe-full"]] | None = None
    conda_recipe_sdist_path: str | None = None

    # conda-build
    conda_build: list[Literal["build", "clean"]] | None = None
    conda_build_run: RUN_ANNO = None


@lru_cache
def parse_posargs(*posargs: str) -> SessionParams:
    """
    Get Parser using `+` for session option prefix.

    Note that using `+` allows for passing underlying `-` options
    without escaping.
    """
    opts = SessionParams.from_posargs(posargs=posargs, prefix_char="+")
    opts.lock = opts.lock or LOCK

    return opts


def add_opts(
    func: Callable[[Session, SessionParams], None],
) -> Callable[[Session], None]:
    """Fill in `opts` from cli options."""

    @wraps(func)
    def wrapped(session: Session) -> None:
        opts = parse_posargs(*session.posargs)
        return func(session, opts)

    return wrapped


def install_dependencies(session: Session, name: str, opts: SessionParams) -> None:
    """General dependencies installer"""
    assert isinstance(session.python, str)  # noqa: S101

    if isinstance(session.virtualenv, CondaEnv):
        environment_file = infer_requirement_path(
            name,
            ext=".yaml",
            python_version=session.python,
            lock=False,
        )
        with check_for_change_manager(
            environment_file,
            hash_path=Path(session.create_tmp()) / "env.json",
        ) as changed:
            if changed or opts.update:
                session.run_install(
                    session.virtualenv.conda_cmd,
                    "env",
                    "update",
                    "--yes",
                    *(["--prune"] if opts.prune else []),
                    "-f",
                    environment_file,
                    "--prefix",
                    session.virtualenv.location,
                )
            else:
                session.log("Using cached install")

    else:
        session.run_install(
            "uv",
            "pip",
            "sync",
            infer_requirement_path(
                name,
                ext=".txt",
                python_version=session.python,
                lock=True,
            ),
        )


# * Environments------------------------------------------------------------------------
# ** requirements
@nox.session(name="requirements", python=False)
@add_opts
def requirements(
    session: Session,
    opts: SessionParams,
) -> None:
    """
    Create environment.yaml and requirement.txt files from pyproject.toml using pyproject2conda.

    These will be placed in the directory "./requirements".
    """
    uvxrun.run(
        "pyproject2conda",
        "project",
        "--verbose",
        *(["--overwrite=force"] if opts.requirements_force else []),
        session=session,
        external=True,
        specs=get_uvxrun_specs(),
    )

    if not opts.requirements_no_notify and opts.lock:
        session.notify("lock")


# ** uv lock compile
@nox.session(name="lock", python=False)
@add_opts
def lock(
    session: Session,
    opts: SessionParams,
) -> None:
    """Run uv pip compile ..."""
    options: list[str] = ["-U"] if opts.lock_upgrade else []
    force = opts.lock_force or opts.lock_upgrade

    reqs_path = Path("./requirements")
    for path in reqs_path.glob("*.txt"):
        python_versions = (
            PYTHON_ALL_VERSIONS
            if path.name in {"test.txt", "typing.txt"}
            else [PYTHON_DEFAULT_VERSION]
        )

        for python_version in python_versions:
            lockpath = infer_requirement_path(
                path.name,
                ext=".txt",
                python_version=python_version,
                lock=True,
                check_exists=False,
            )

            with check_for_change_manager(
                path,
                target_path=lockpath,
                force_write=force,
            ) as changed:
                if force or changed:
                    session.run(
                        "uv",
                        "pip",
                        "compile",
                        "--universal",
                        "-q",
                        "-p",
                        python_version,
                        *options,
                        path,
                        "-o",
                        lockpath,
                    )
                else:
                    session.log(f"Skipping {lockpath}")


# ** testing
def _test(
    session: nox.Session,
    run: RUN_TYPE,
    test_no_pytest: bool,
    test_opts: OPT_TYPE,
    no_cov: bool,
) -> None:
    import os

    tmpdir = os.environ.get("TMPDIR", None)

    session_run_commands(session, run)
    if not test_no_pytest:
        opts = combine_list_str(test_opts or [])
        if not no_cov:
            session.env["COVERAGE_FILE"] = str(Path(session.create_tmp()) / ".coverage")

            if not any(o.startswith("--cov") for o in opts):
                opts.append(f"--cov={IMPORT_NAME}")

        # Because we are testing if temporary folders
        # have git or not, we have to make sure we're above the
        # not under this repo
        # so revert to using the top level `TMPDIR`
        if tmpdir:
            session.env["TMPDIR"] = tmpdir

        session.run("pytest", *opts)


# *** Basic tests
@add_opts
def test(
    session: Session,
    opts: SessionParams,
) -> None:
    """Test environments with conda installs."""
    install_dependencies(session, "test", opts)
    session.run(
        "uv",
        "pip",
        "install",
        get_package_wheel(session),
        "--no-deps",
        "--force-reinstall",
        external=True,
    )

    _test(
        session=session,
        run=opts.test_run,
        test_no_pytest=opts.test_no_pytest,
        test_opts=opts.test_opts,
        no_cov=opts.no_cov,
    )


nox.session(**ALL_KWS)(test)
nox.session(name="test-conda", **CONDA_ALL_KWS)(test)


@nox.session(name="test-sync", **ALL_KWS)
@add_opts
def test_sync(session: Session, opts: SessionParams) -> None:
    """Run tests using uv sync ..."""
    session.run_install(
        "uv",
        "sync",
        "--no-dev",
        "--group",
        "test",
        # Handle package install here?
        # "--no-editable",
        # "--reinstall-package",
        # "open-notebook",
        "--no-install-project",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    # handle package install separately
    session.run(
        "uv",
        "pip",
        "install",
        get_package_wheel(session),
        "--no-deps",
        "--force-reinstall",
    )

    _test(
        session=session,
        run=opts.test_run,
        test_no_pytest=opts.test_no_pytest,
        test_opts=opts.test_opts,
        no_cov=opts.no_cov,
    )


@nox.session(name="test-notebook", **DEFAULT_KWS)
@add_opts
def test_notebook(session: nox.Session, opts: SessionParams) -> None:
    """Run pytest --nbval."""
    install_dependencies(session, "test-notebook", opts)
    session.run_always(
        "uv",
        "pip",
        "install",
        get_package_wheel(session),
        "--no-deps",
        "--force-reinstall",
    )

    test_nbval_opts = shlex.split(
        """
    --nbval
    --nbval-current-env
    --nbval-sanitize-with=config/nbval.ini
    --dist loadscope
     examples/usage
   """,
    )

    test_opts = (opts.test_opts or []) + test_nbval_opts

    session.log(f"{test_opts = }")

    _test(
        session=session,
        run=opts.test_run,
        test_no_pytest=opts.test_no_pytest,
        test_opts=test_opts,
        no_cov=opts.no_cov,
    )


@nox.session(python=False)
@add_opts
def coverage(
    session: Session,
    opts: SessionParams,
) -> None:
    """Run coverage."""
    cmd = opts.coverage or ["combine", "html", "report"]

    run = partial(uvxrun.run, specs=get_uvxrun_specs(), session=session)

    paths = list(Path(".nox").glob("test-*/tmp/.coverage*"))

    if "erase" in cmd:
        for path in paths:
            if path.exists():
                session.log(f"removing {path}")
                path.unlink()

    for c in cmd:
        if c == "combine":
            run(
                "coverage",
                "combine",
                "--keep",
                "-a",
                *paths,
            )
        elif c == "open":
            open_webpage(path="htmlcov/index.html")

        else:
            run(
                "coverage",
                c,
            )


# *** testdist (conda)
@add_opts
def testdist(
    session: Session,
    opts: SessionParams,
) -> None:
    """Test conda distribution."""
    install_str = PACKAGE_NAME
    if opts.version:
        install_str = f"{install_str}=={opts.version}"

    install_dependencies(session, "test-extras", opts)

    if isinstance(session.virtualenv, CondaEnv):
        session.conda_install(install_str)
    else:
        session.install(install_str)

    _test(
        session=session,
        run=opts.testdist_run,
        test_no_pytest=opts.test_no_pytest,
        test_opts=opts.test_opts,
        no_cov=opts.no_cov,
    )


nox.session(name="testdist-pypi", **ALL_KWS)(testdist)
nox.session(name="testdist-conda", **CONDA_ALL_KWS)(testdist)


# # ** Docs
@nox.session(name="docs", **DEFAULT_KWS)
@add_opts
def docs(
    session: nox.Session,
    opts: SessionParams,
) -> None:
    """
    Run `make` in docs directory.

    For example, 'nox -s docs -- +d html'
    calls 'make -C docs html'. With 'release' option, you can set the
    message with 'message=...' in posargs.
    """
    install_dependencies(session, "docs", opts)
    session.install("-e", ".", "--no-deps")

    if opts.version:
        session.env["SETUPTOOLS_SCM_PRETEND_VERSION"] = opts.version
    session_run_commands(session, opts.docs_run)

    cmd = opts.docs or []
    cmd = ["html"] if not opts.docs_run and not cmd else list(cmd)

    if "symlink" in cmd:
        cmd.remove("symlink")
        _create_doc_examples_symlinks(session)

    if open_page := "open" in cmd:
        cmd.remove("open")

    if serve := "serve" in cmd:
        open_webpage(url="http://localhost:8000")
        cmd.remove("serve")

    if cmd:
        args = ["make", "-C", "docs", *combine_list_str(cmd)]
        session.run(*args, external=True)

    if open_page:
        open_webpage(path="./docs/_build/html/index.html")

    if serve and "livehtml" not in cmd:
        session.run(
            "python",
            "-m",
            "http.server",
            "-d",
            "docs/_build/html",
            "-b",
            "127.0.0.1",
            "8000",
        )


# ** lint
@nox.session(python=False)
def lint(
    session: nox.Session,
) -> None:
    """
    Run linters with pre-commit.

    Defaults to `pre-commit run --all-files`.
    To run something else pass, e.g.,
    `nox -s lint -- --lint-run "pre-commit run --hook-stage manual --all-files`
    """
    uvxrun.run(
        "pre-commit",
        "run",
        "--all-files",  # "--show-diff-on-failure",
        specs=get_uvxrun_specs(),
        session=session,
    )


# ** type checking
@nox.session(name="typing", **ALL_KWS)
@add_opts
def typing(  # noqa: C901
    session: nox.Session,
    opts: SessionParams,
) -> None:
    """Run type checkers (mypy, pyright, pytype)."""
    install_dependencies(session, "typing", opts)
    session.install("-e", ".", "--no-deps")

    session_run_commands(session, opts.typing_run)

    cmd = opts.typing or []
    if not opts.typing_run and not opts.typing_run_internal and not cmd:
        cmd = ["mypy", "pyright"]

    if "all" in cmd:
        cmd = ["mypy", "pyright", "pytype"]

    # set the cache directory for mypy
    session.env["MYPY_CACHE_DIR"] = str(Path(session.create_tmp()) / ".mypy_cache")

    if "clean" in cmd:
        cmd = list(cmd)
        cmd.remove("clean")

        for name in [".mypy_cache", ".pytype"]:
            p = Path(session.create_tmp()) / name
            if p.exists():
                session.log(f"removing cache {p}")
                shutil.rmtree(str(p))

    if not isinstance(session.python, str):
        raise TypeError

    run = partial(
        uvxrun.run,
        specs=get_uvxrun_specs(UVXRUN_LOCK_REQUIREMENTS),
        session=session,
        python_version=session.python,
        python_executable=get_python_full_path(session),
        external=True,
    )

    for c in cmd:
        if c.endswith("-notebook"):
            session.run("make", c, external=True)
        elif c == "mypy":
            run("mypy", "--color-output")
        elif c == "pyright":
            run("pyright")
        else:
            session.log(f"Skipping unknown command {c}")

    for cmds in combine_list_list_str(opts.typing_run_internal or []):
        run(*cmds)


# ** Dist pypi
# NOTE: you can skip having the build environment and
# just use uv build, but faster to use environment ...
USE_ENVIRONMENT_FOR_BUILD = False
_build_dec = nox.session if USE_ENVIRONMENT_FOR_BUILD else nox.session(python=False)


@_build_dec
@add_opts
def build(session: nox.Session, opts: SessionParams) -> None:  # noqa: C901
    """
    Build the distribution.

    Note that default is to not use build isolation.
    Pass `--build-isolation` to use build isolation.
    """
    if USE_ENVIRONMENT_FOR_BUILD:
        install_dependencies(session, "build", opts)

    if opts.version:
        session.env["SETUPTOOLS_SCM_PRETEND_VERSION"] = opts.version

    for cmd in opts.build or ["build"]:
        if cmd == "version":
            if USE_ENVIRONMENT_FOR_BUILD:
                session.run(get_python_full_path(session), "-m", "hatchling", "version")  # pyright: ignore[reportPossiblyUnboundVariable]
            else:
                session.run(
                    "uvx", "--with", "hatch-vcs", "hatchling", "version", external=True
                )
        elif cmd == "build":
            outdir = opts.build_outdir
            if Path(outdir).exists():
                shutil.rmtree(outdir)

            args = f"uv build --out-dir {outdir}".split()
            if USE_ENVIRONMENT_FOR_BUILD and not opts.build_isolation:
                args.append("--no-build-isolation")

            if opts.build_opts:
                args.extend(opts.build_opts)

            out = session.run(*args, silent=opts.build_silent)
            if opts.build_silent:
                if not isinstance(out, str):
                    msg = "session.run output not a string"
                    raise ValueError(msg)
                session.log(out.strip().split("\n")[-1])


def get_package_wheel(
    session: Session,
    opts: str | Iterable[str] | None = None,
    extras: str | Iterable[str] | None = None,
    reuse: bool = True,
) -> str:
    """
    Build the package in return the build location

    This is similar to how tox does isolated builds.

    Note that the first time this is called,

    Should be straightforward to extend this to isolated builds
    that depend on python version (something like have session build-3.11 ....)
    """
    dist_location = Path(session.cache_dir) / "dist"
    if reuse and getattr(get_package_wheel, "_called", False):
        session.log("Reuse isolated build")
    else:
        cmd = f"nox -s build -- ++build-outdir {dist_location} ++build-opts --wheel ++build-silent"
        session.run_always(*shlex.split(cmd), external=True)

        # save that this was called:
        if reuse:
            get_package_wheel._called = True  # type: ignore[attr-defined]  # noqa: SLF001

    paths = list(dist_location.glob("*.whl"))
    if len(paths) != 1:
        msg = f"something wonky with paths {paths}"
        raise ValueError(msg)

    path = f"{PACKAGE_NAME}@{paths[0]}"
    if extras:
        if not isinstance(extras, str):
            extras = ",".join(extras)
        path = f"{path}[{extras}]"

    if opts:
        if not isinstance(opts, str):
            opts = " ".join(opts)
        path = f"{path} {opts}"

    return path


@nox.session(python=False)
@add_opts
def publish(session: nox.Session, opts: SessionParams) -> None:
    """Publish the distribution"""
    run = partial(uvxrun.run, specs=get_uvxrun_specs(), session=session, external=True)

    for cmd in opts.publish or []:
        if cmd == "test":
            run("twine", "upload", "--repository", "testpypi", "dist/*")
        elif cmd == "release":
            run("twine", "upload", "dist/*")
        elif cmd == "check":
            run("twine", "check", "--strict", "dist/*")


# # ** Dist conda
@nox.session(name="conda-recipe", python=False)
@add_opts
def conda_recipe(
    session: nox.Session,
    opts: SessionParams,
) -> None:
    """Run grayskull to create recipe"""
    commands = opts.conda_recipe or ["recipe"]

    run = partial(uvxrun.run, specs=get_uvxrun_specs(), session=session)

    if not (sdist_path := opts.conda_recipe_sdist_path):
        sdist_path = PACKAGE_NAME
        if opts.version:
            sdist_path = f"{sdist_path}=={opts.version}"

    for command in commands:
        if command == "recipe":
            # make directory?
            if not (d := Path("./dist-conda")).exists():
                d.mkdir()

            run(
                "grayskull",
                "pypi",
                sdist_path,
                "--sections",
                "package",
                "source",
                "build",
                "requirements",
                "-o",
                "dist-conda",
            )

            _append_recipe(
                f"dist-conda/{PACKAGE_NAME}/meta.yaml",
                "config/recipe-append.yaml",
            )
            session.run("cat", f"dist-conda/{PACKAGE_NAME}/meta.yaml", external=True)

        elif command == "recipe-full":
            import tempfile

            with tempfile.TemporaryDirectory() as d:  # type: ignore[assignment,unused-ignore]
                run(
                    "grayskull",
                    "pypi",
                    sdist_path,
                    "-o",
                    str(d),
                )
                path = Path(d) / PACKAGE_NAME / "meta.yaml"
                session.log(f"cat {path}:")
                with path.open() as f:
                    for line in f:
                        print(line, end="")  # noqa: T201


@nox.session(name="conda-build", **CONDA_DEFAULT_KWS)
@add_opts
def conda_build(session: nox.Session, opts: SessionParams) -> None:
    """Run `conda mambabuild`."""
    session.conda_install("boa", "anaconda-client")
    cmds, run = opts.conda_build, opts.conda_build_run

    session_run_commands(session, run)

    if not run and not cmds:
        cmds = ["build", "clean"]

    if cmds is None:
        cmds = []

    cmds = list(cmds)
    if "clean" in cmds:
        cmds.remove("clean")
        session.log("removing directory dist-conda/build")
        if Path("./dist-conda/build").exists():
            shutil.rmtree("./dist-conda/build")

    for cmd in cmds:
        if cmd == "build":
            if not (d := Path(f"./dist-conda/{PACKAGE_NAME}/meta.yaml")).exists():
                msg = f"no file {d}"
                raise ValueError(msg)

            session.run(
                "conda",
                "mambabuild",
                "--output-folder=dist-conda/build",
                "--no-anaconda-upload",
                "dist-conda",
            )


# ** Other utilities
@nox.session
@add_opts
def cog(session: nox.Session, opts: SessionParams) -> None:  # noqa: ARG001
    """Run cog."""
    session.install("cogapp")
    session.run("cog", "-rP", "README.md", env={"COLUMNS": "90"})


# * Utilities -------------------------------------------------------------------------
def _create_doc_examples_symlinks(session: nox.Session, clean: bool = True) -> None:  # noqa: C901
    """Create symlinks from docs/examples/*.md files to /examples/usage/..."""
    import os

    def usage_paths(path: Path) -> Iterator[Path]:
        with path.open("r") as f:
            for line in f:
                if line.startswith("usage/"):
                    yield Path(line.strip())

    def get_target_path(
        usage_path: str | Path,
        prefix_dir: str | Path = "./examples",
        exts: Sequence[str] = (".md", ".ipynb"),
    ) -> Path:
        path = Path(prefix_dir) / Path(usage_path)

        if not all(ext.startswith(".") for ext in exts):
            msg = "Bad extensions.  Should start with '.'"
            raise ValueError(msg)

        if path.exists():
            return path

        for ext in exts:
            p = path.with_suffix(ext)
            if p.exists():
                return p

        msg = f"no path found for base {path}"
        raise ValueError(msg)

    root = Path("./docs/examples/")
    if clean:
        import shutil

        shutil.rmtree(root / "usage", ignore_errors=True)

    # get all md files
    paths = list(root.glob("*.md"))

    # read usage lines
    for path in paths:
        for usage_path in usage_paths(path):
            target = get_target_path(usage_path)
            link = root / usage_path.parent / target.name

            if link.exists():
                link.unlink()

            link.parent.mkdir(parents=True, exist_ok=True)

            target_rel = os.path.relpath(target, start=link.parent)
            session.log(f"linking {target_rel} -> {link}")

            os.symlink(target_rel, link)


def _append_recipe(recipe_path: str | Path, append_path: str | Path) -> None:
    recipe_path = Path(recipe_path)
    append_path = Path(append_path)

    with recipe_path.open() as f:
        recipe = f.readlines()

    with append_path.open() as f:
        append = f.readlines()

    with recipe_path.open("w") as f:
        f.writelines([*recipe, "\n", *append])
