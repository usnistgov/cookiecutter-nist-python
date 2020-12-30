"""
.. currentmodule: {{ cookiecutter.project_name }}

Top level stuff
===============

.. autosummary::
   :toctree: generated/

   a_function - a test function
   another_func - another test fuction
"""
import pkg_resources

from .{{ cookiecutter.project_slug }} import a_function
from .core import another_func

try:
    __version__ = pkg_resources.get_distribution("{{ cookiecutter.project_name }}").version
except Exception:
    # Local copy or not installed with setuptools.
    # Disable minimum version checks on downstream libraries.
    __version__ = "999"

__author__ = """{{ cookiecutter.full_name }}"""
__email__ = '{{ cookiecutter.email }}'
