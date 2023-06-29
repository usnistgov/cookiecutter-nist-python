"""
.. currentmodule: {{ cookiecutter.project_slug }}

Top level stuff
===============

.. autosummary::
   :toctree: generated/

   a_function - a test function
   another_func - another test fuction
"""

from .core import another_func
from .{{ cookiecutter.project_slug }} import a_function

# updated versioning scheme
try:
    from ._version import __version__
except Exception:
    __version__ = "999"


__author__ = """{{ cookiecutter.full_name }}"""
__email__ = "{{ cookiecutter.email }}"


__all__ = [
    "a_function",
    "another_func",
]
