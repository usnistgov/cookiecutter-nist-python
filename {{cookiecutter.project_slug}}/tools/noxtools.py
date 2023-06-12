"""Utilities to work with nox"""

from __future__ import annotations

import shlex
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, Literal, cast

from ruamel.yaml import safe_load

if TYPE_CHECKING:
    from collections.abc import Collection, Sequence

    import nox


# --- Basic utilities -------------------------------------------------------------------
def combine_list_str(opts: list[str]) -> list[str]:
    if opts:
        return shlex.split(" ".join(opts))
    else:
        return []


def combine_list_list_str(opts: list[list[str]]) -> Iterable[list[str]]:
    return (combine_list_str(opt) for opt in opts)


def sort_like(values: Collection[Any], like: Sequence[Any]) -> list[Any]:
    """Sort `values` in order of `like`."""
    # only unique
    sorter = {k: i for i, k in enumerate(like)}
    return sorted(set(values), key=lambda k: sorter[k])


def update_target(target: str | Path, *deps: str | Path) -> bool:
    """Check if target is older than deps:"""

    target_path = Path(target)

    deps_path = tuple(map(Path, deps))

    for d in deps_path:
        if not d.exists():
            raise ValueError(f"dependency {d} does not exist")

    if not target_path.exists():
        update = True

    else:
        target_time = target_path.stat().st_mtime
        update = any(target_time < dep.stat().st_mtime for dep in deps_path)

    return update


def prepend_flag(flag: str, *args: str) -> list[str]:
    """
    Add in a flag before each arg.

    >>> prepent_flag("-k", "a", "b")
    ["-k", "a", "-k", "b"]

    """

    if len(args) == 1 and not isinstance(args[0], str):
        args = args[0]

    return sum([[flag, _] for _ in args], [])


# --- Nox session utilities ------------------------------------------------------------
def session_skip_install(session: nox.Session) -> bool:
    """
    Utility to check if we're skipping install and reusing existing venv
    This is a hack and may need to change if upstream changes.
    """
    return session._runner.global_config.no_install and session._runner.venv._reused  # type: ignore


def session_run_commands(
    session: nox.Session, commands: list[list[str]], external: bool = True, **kws: Any
) -> None:
    """Run commands command"""

    if commands:
        kws.update(external=external)
        for opt in combine_list_list_str(commands):
            session.run(*opt, **kws)


def session_set_ipykernel_display_name(
    session: nox.Session, display_name: str | None, check_skip_install: bool = True
) -> None:
    """Rename ipython kernel display name."""
    if not display_name or (check_skip_install and session_skip_install(session)):
        return
    else:
        command = f"python -m ipykernel install --sys-prefix --display-name {display_name}".split()
        # continue if fails
        session.run(*command, success_codes=[0, 1])


def session_install_package(
    session: nox.Session,
    package: str = ".",
    develop: bool = True,
    no_deps: bool = True,
    *args: str,
    **kwargs: Any,
) -> None:
    """Install package into session."""

    if session_skip_install(session):
        return

    if develop:
        command = ["-e"]
    else:
        command = []

    command.append(package)

    if no_deps:
        command.append("--no-deps")

    session.install(*command, *args, **kwargs)


# --- Create env from lock -------------------------------------------------------------


def session_install_envs_lock(
    session: nox.Session,
    lockfile: str | Path,
    extras: str | list[str] | None = None,
    display_name: str | None = None,
    force_reinstall: bool = False,
    install_package: bool = False,
) -> bool:
    """Install depedencies using conda-lock"""

    if session_skip_install(session):
        return True

    unchanged, hashes = env_unchanged(
        session, lockfile, prefix="lock", other=dict(install_package=install_package)
    )
    if unchanged and not force_reinstall:
        return unchanged

    if extras:
        if isinstance(extras, str):
            extras = extras.split(",")
        extras = cast(list[str], sum([["--extras", _] for _ in extras], []))
    else:
        extras = []

    session.run(
        "conda-lock",
        "install",
        "--mamba",
        *extras,
        "-p",
        str(session.virtualenv.location),
        str(lockfile),
        silent=True,
        external=True,
    )

    if install_package:
        session_install_package(session)

    session_set_ipykernel_display_name(session, display_name)

    write_hashfile(hashes, session=session, prefix="lock")

    return unchanged


# --- create env from yaml -------------------------------------------------------------


def parse_envs(
    *paths: str | Path,
    remove_python: bool = True,
    deps: Collection[str] | None = None,
    reqs: Collection[str] | None = None,
    channels: Collection[str] | None = None,
) -> tuple[set[str], set[str], set[str], str | None]:
    """Parse an `environment.yaml` file."""

    def _default(x) -> set[str]:
        if x is None:
            return set()
        elif isinstance(x, str):
            x = [x]
        return set(x)

    channels = _default(channels)
    deps = _default(deps)
    reqs = _default(reqs)
    name = None

    def _get_context(path):
        if hasattr(path, "readline"):
            from contextlib import nullcontext

            return nullcontext(path)
        else:
            return Path(path).open("r")

    for path in paths:
        with _get_context(path) as f:
            data = safe_load(f)

        channels.update(data.get("channels", []))
        name = data.get("name", name)

        # check dependencies for pip
        for d in data.get("dependencies", []):
            if isinstance(d, dict):
                reqs.update(cast(list[str], d.get("pip")))
            else:
                if remove_python and d[: len("python")] != "python":
                    deps.add(d)

    return channels, deps, reqs, name


def session_install_envs(
    session: nox.Session,
    *paths: str | Path,
    remove_python: bool = True,
    deps: Collection[str] | None = None,
    reqs: Collection[str] | None = None,
    channels: Collection[str] | None = None,
    conda_install_kws: dict[str, Any] | None = None,
    install_kws: dict[str, Any] | None = None,
    display_name: str | None = None,
    force_reinstall: bool = False,
    install_package: bool = False,
) -> bool:
    """Parse and install everything. Pass an already merged yaml file."""

    if session_skip_install(session):
        return True

    unchanged, hashes = env_unchanged(
        session,
        *paths,
        prefix="env",
        other=dict(
            deps=deps, reqs=reqs, channels=channels, install_package=install_package
        ),
    )
    if unchanged and not force_reinstall:
        return unchanged

    channels, deps, reqs, name = parse_envs(
        *paths,
        remove_python=remove_python,
        deps=deps,
        reqs=reqs,
        channels=channels,
    )

    if not channels:
        channels = ""
    if deps:
        conda_install_kws = conda_install_kws or {}
        conda_install_kws.update(channel=channels)
        session.conda_install(*deps, **(conda_install_kws or {}))

    if reqs:
        session.install(*reqs, **(install_kws or {}))

    if install_package:
        session_install_package(session)

    session_set_ipykernel_display_name(session, display_name)

    write_hashfile(hashes, session=session, prefix="env")

    return unchanged


def session_install_pip(
    session: nox.Session,
    requirement_paths: Collection[str] | None = None,
    constraint_paths: Collection[str] | None = None,
    extras: str | Collection[str] | None = None,
    reqs: Collection[str] | None = None,
    display_name: str | None = None,
    force_reinstall: bool = False,
    install_package: bool = False,
    no_deps: bool = False,
):
    if session_skip_install(session):
        return True

    if extras:
        install_package = True
        if not isinstance(extras, str):
            extras = ",".join(extras)
        install_package_args = ["-e", f".[{extras}]"]
    elif install_package:
        install_package_args = ["-e", "."]

    if install_package and no_deps:
        install_package_args.append("--no-deps")

    requirement_paths = requirement_paths or ()
    constraint_paths = constraint_paths or ()
    reqs = reqs or ()
    paths = requirement_paths + constraint_paths

    unchanged, hashes = env_unchanged(
        session,
        *paths,
        prefix="pip",
        other=dict(
            reqs=reqs, extras=extras, install_package=install_package, no_deps=no_deps
        ),
    )

    if unchanged and not force_reinstall:
        return unchanged

    install_args = (
        prepend_flag("-r", *requirement_paths)
        + prepend_flag("-c", *constraint_paths)
        + list(reqs)
    )

    if install_args:
        session.install(*install_args)

    if install_package:
        session.install(*install_package_args)

    session_set_ipykernel_display_name(session, display_name)

    write_hashfile(hashes, session=session, prefix="pip")


def session_install_envs_merge(
    session,
    *paths,
    remove_python=True,
    deps=None,
    reqs=None,
    channels=None,
    conda_install_kws=None,
    install_kws=None,
    display_name=None,
    force_reinstall=False,
) -> bool:
    """Merge files (using conda-merge) and then create env"""

    if session_skip_install(session):
        return True

    unchanged, hashes = env_unchanged(
        session, *paths, prefix="env", other=dict(deps=deps, reqs=reqs)
    )
    if unchanged and not force_reinstall:
        return unchanged

    # first create a temporary file for the environment
    with tempfile.TemporaryDirectory() as d:
        yaml = Path(d) / "tmp_env.yaml"
        with yaml.open("w") as f:
            session.run("conda-merge", *paths, stdout=f, external=True)
        session.run("cat", str(yaml), external=True, silent=True)

        channels, deps, reqs, _ = parse_envs(
            yaml, remove_python=remove_python, deps=deps, reqs=reqs, channels=channels
        )

    if deps:
        if conda_install_kws is None:
            conda_install_kws = {}
        conda_install_kws.update(channel=channels)
        session.conda_install(*deps, **conda_install_kws)

    if reqs:
        if install_kws is None:
            install_kws = {}
        session.install(*reqs, **install_kws)

    session_set_ipykernel_display_name(session, display_name)

    write_hashfile(hashes, session=session, prefix="env")

    return unchanged


# --- Hash environment -----------------------------------------------------------------

PREFIX_HASH_EXTS = Literal["env", "lock", "pip"]


def env_unchanged(
    session: nox.Session,
    *paths: str | Path,
    prefix: PREFIX_HASH_EXTS,
    verbose: bool = True,
    hashes: dict[str, str] | None = None,
    other: Any | None = None,
) -> tuple[bool, dict[str, str]]:
    hashfile = hashfile_path(session, prefix)

    if hashes is None:
        hashes = get_hashes(*paths, other=other)

    if hashfile.exists():
        if verbose:
            session.log(f"hash file {hashfile} exists")
        unchanged = hashes == read_hashfile(hashfile)
    else:
        unchanged = False

    if unchanged:
        session.log(f"session {session.name} unchanged")
    else:
        session.log(f"session {session.name} changed")

    return unchanged, hashes


def get_hashes(
    *paths: str | Path,
    other: str | None = None,
) -> dict[str, str]:
    """Get md5 hashes for paths"""
    out = {str(path): _get_file_hash(path) for path in paths}

    if other:
        import hashlib

        out["other"] = hashlib.md5(str(other).encode("utf-8")).hexdigest()
    return out


def hashfile_path(session: nox.Session, prefix: PREFIX_HASH_EXTS) -> Path:
    """Path for hashfile for this session"""
    return Path(session.create_tmp()) / f"{prefix}.json"


def write_hashfile(
    hashes: dict[str, str],
    session: nox.Session,
    prefix: PREFIX_HASH_EXTS,
) -> None:
    import json

    path = hashfile_path(session, prefix)

    with open(path, "w") as f:
        json.dump(hashes, f)


def read_hashfile(
    path: str | Path,
) -> dict[str, str]:
    import json

    with open(path) as f:
        data = json.load(f)
    return cast(dict[str, str], data)


def _get_file_hash(path: str | Path, buff_size=65536) -> str:
    import hashlib

    md5 = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            data = f.read(buff_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


# from contextlib import contextmanager
# @contextmanager
# def check_hashed_env(
#         session: nox.Session,
#         *paths: str | Path,
#         prefix: Literal["env", "lock"],
#         verbose: bool=True,
#         recreate_session=False,
# ):

#     changed, hashes = env_hashes_changed(session, *paths, prefix, verbose=verbose, return_hashes=True)


#     if changed and recreate_session:
#         if verbose:
#             session.log("env changed.  Recreating {session.virtualenv.location_name}")
#             _reuse_original = session.virtualenv.reuse_existing
#             _no_install_original = session._runner.global_config.no_install

#             session.virtualenv.reuse_existing = False
#             session._runner.global_config.no_install = False

#             session.virtualenv.create()
#             env_hashes_changed(session, *paths, prefix, verbose=verbose, hashes=hashes)

#             session.virtualenv.reuse_existing = _reuse_original


# def _remove_python_from_yaml(path):
#     from yaml import safe_dump

#     path = Path(path)

#     with path.open("r") as f:
#         data = safe_load(f)

#     from copy import deepcopy

#     out = deepcopy(data)

#     for dep in list(out["dependencies"]):
#         if isinstance(dep, str) and dep[: len("python")] == "python":
#             out["dependencies"].remove(dep)

#     path_out = path.with_suffix(".final.yaml")

#     with path_out.open("w") as f:
#         safe_dump(out, f)

#     return path_out


# def session_install_envs_update(
#     session: nox.Session,
#     conda_backend: str,
#     *paths: str | Path,
#     remove_python: bool = True,
#     deps: Sequence[str] | None = None,
#     reqs: Sequence[str] | None = None,
#     conda_install_kws: Mapping[str, str] | None = None,
#     install_kws: Mapping[str, str] | None = None,
#     display_name: str | None = None,
# ) -> None:
#     """Install multiple 'environment.yaml' files."""

#     if session_skip_install(session):
#         return

#     from shutil import which

#     if not which("conda-merge"):
#         session.conda_install("conda-merge")

#     # pin the python version

#     with tempfile.TemporaryDirectory() as d:
#         yaml = Path(d) / "tmp_env.yaml"
#         with yaml.open("w") as f:
#             session.run("conda-merge", *paths, stdout=f, external=True)

#         if remove_python:
#             yaml = _remove_python_from_yaml(yaml)

#         session.run("cat", str(yaml), external=True, silent=False)

#         session.run(
#             conda_backend,
#             "env",
#             "update",
#             "--prefix",
#             session.virtualenv.location,
#             "--file",
#             str(yaml),
#             silent=True,
#             external=True,
#         )

#     session_set_ipykernel_display_name(session, display_name)


# def pin_python_version(session: nox.Session):
#     path = Path(session.virtualenv.location) / "conda-meta" / "pinned"

#     with path.open("w") as f:
#         session.run(
#             "python",
#             "-c",
#             """import sys; print("python=={v.major}.{v.minor}.{v.micro}".format(v=sys.version_info))""",
#             stdout=f,
#         )

# def session_install_envs_update_pin(
#     session: nox.Session,
#     conda_backend: str,
#     *paths: str | Path,
#         display_name: str | None = None,
#     **kws,
# ) -> None:
#     """Install multiple 'environment.yaml' files."""

#     if session_skip_install(session):
#         return

#     from shutil import which

#     if not which("conda-merge"):
#         session.conda_install("conda-merge")

#     # pin the python version
#     pin_python_version(session)

#     with tempfile.TemporaryDirectory() as d:
#         yaml = Path(d) / "tmp_env.yaml"
#         with yaml.open("w") as f:
#             session.run("conda-merge", *paths, stdout=f, external=True)

#         session.run("cat", str(yaml), external=True, silent=False)

#         session.run(
#             conda_backend,
#             "env",
#             "update",
#             "--prefix",
#             session.virtualenv.location,
#             "--file",
#             str(yaml),
#             silent=True,
#             external=True,
#             **kws,
#         )

#     session_set_ipykernel_display_name(session, display_name)


# def parse_args_for_flag(args, flag, action="value"):
#     """
#     Parse args for flag and pop it off args

#     Parameters
#     ----------
#     args : iterable
#         For example, session.posargs.
#     flag : string
#         For example, `flag='--run-external'
#     action : {'value', 'values', 'store_true', 'store_false'}

#     If flag can take multiple values, they should be separated by commas

#     If multiples, return a tuple, else return a string.
#     """
#     flag = flag.strip()
#     n = len(flag)

#     def process_value(arg):
#         if action == "store_true":
#             value = True
#         elif action == "store_false":
#             value = False
#         else:
#             s = arg.split("=")
#             if len(s) != 2:
#                 raise ValueError(f"must supply {flag}=value")
#             if action == "value":
#                 value = s[-1].strip()
#             else:
#                 value = tuple(_.strip() for _ in s[-1].split(","))

#         return value

#     def check_for_flag(arg):
#         s = arg.strip()
#         if action.startswith("value"):
#             return s[:n] == f"{flag}"
#         else:
#             return s == flag

#     # initial value
#     if action == "store_true":
#         value = False
#     elif action == "store_false":
#         value = True
#     elif action in ["value", "values"]:
#         value = None
#     else:
#         raise ValueError(
#             f"action {action} must be one of [store_true, store_false, value, values]"
#         )

#     out = []
#     for arg in args:
#         if check_for_flag(arg):
#             value = process_value(arg)
#         else:
#             out.append(arg)

#     return value, out


# def parse_args_run_external(args):
#     """Parse (and pop) for --run-external flag"""
#     return parse_args_for_flag(args, flag="--run-external", action="store_true")


# def parse_args_test_version(args):
#     """Parse for flag --test-version=..."""
#     return parse_args_for_flag(args, flag="--test-version", action="value")


# def parse_args_pip_extras(args, default=None, join=True):
#     """Parse for flag '--pip-extras=..."""
#     extras, args = parse_args_for_flag(args, flag="--pip-extras", action="values")

#     if extras:
#         extras = set(extras)

#     if default:
#         if extras is None:
#             extras = set()
#         if isinstance(default, str):
#             default = (default,)
#         for d in default:
#             extras.update(d.split(","))

#     if extras and join:
#         extras = ",".join(extras)

#     return extras, args


# def check_args_with_default(args, default=None):
#     """If no args and have a default, place it in args."""
#     if not args and default:
#         if isinstance(default, str):
#             default = default.split()
#         args = default
#     return args


# def run_with_external_check(
#     session, args=None, default=None, check_run_external=True, **kws
# ):
#     """
#     Use session.run with session.posargs.
#     Perform `seesion.run(*args)`, where `args` comes from posargs.
#     If no posargs, then use default.
#     Also, check for flag '--run-external'.  If present,
#     call `session.run(*args, external=True)`
#     """

#     if args is None:
#         args = session.posargs

#     if check_run_external:
#         external, args = parse_args_run_external(args)
#     else:
#         external = False

#     args = check_args_with_default(args, default=default)

# #     session.log(f"args {args}")
# #     session.log(f"external {external}")
# #     session.run(*args, external=external, **kws)
