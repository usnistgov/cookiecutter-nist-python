#!/usr/bin/env python

"""Tests for `{{ cookiecutter.project_name }}` package."""

import pytest
{%- if cookiecutter.command_line_interface|lower in ["click", "typer"] %}
from click.testing import CliRunner
{%- endif %}

from {{ cookiecutter.project_slug }} import example_function
{%- if cookiecutter.command_line_interface|lower in ["click", "typer"] %}
from {{ cookiecutter.project_slug }} import cli
{%- endif %}


@pytest.fixture
def response():
    return 1, 2


def test_example_function(response):
    assert example_function(*response) == 3
{%- if cookiecutter.command_line_interface|lower in ["click", "typer"] %}


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert "{{ cookiecutter.project_slug }}.cli.main" in result.output
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help" in help_result.output
    assert "Show this message and exit." in help_result.output
{%- endif %}
