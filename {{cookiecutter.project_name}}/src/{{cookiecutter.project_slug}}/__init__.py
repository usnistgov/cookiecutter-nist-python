"""
Top level API (:mod:`{{ cookiecutter.project_slug }}`)
======================================================
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from .core import example_function

try:  # noqa: RUF067
    __version__ = _version("{{ cookiecutter.project_name }}")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "999"


__author__ = """{{ cookiecutter.full_name }}"""


__all__ = [
    "__version__",
    "example_function",
]
