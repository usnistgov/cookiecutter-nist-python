"""Top-level package for {{ cookiecutter.project_name }}."""

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

__author__ = """{{ cookiecutter.full_name }}"""
__email__ = '{{ cookiecutter.email }}'
