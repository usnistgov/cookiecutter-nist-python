"""
Top level API (:mod:`{{ cookiecutter.project_slug }}`)
======================================================
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from .core import example_function

try:
    __version__ = _version("{{ cookiecutter.project_slug }}")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "999"


__author__ = """{{ cookiecutter.full_name }}"""
__email__ = "{{ cookiecutter.email }}"


__all__ = [
    "example_function",
    "__version__",
]
