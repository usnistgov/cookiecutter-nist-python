"""
Top level API (:mod:`{{ cookiecutter.project_slug }}`)
======================================================
"""

from .core import example_function

try:
    from ._version import __version__  # type: ignore[unused-ignore,import]
except Exception:  # pragma: no cover
    __version__ = "999"

__author__ = """{{ cookiecutter.full_name }}"""
__email__ = "{{ cookiecutter.email }}"


__all__ = [
    "example_function",
    "__version__",
]
