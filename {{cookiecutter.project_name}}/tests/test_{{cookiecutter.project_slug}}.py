"""Tests for `{{ cookiecutter.project_name }}` package."""

from __future__ import annotations

import pytest
{%- if cookiecutter.command_line_interface in ["click", "typer"] %}
from click.testing import CliRunner
{%- endif %}
{% if cookiecutter.command_line_interface in ["click", "typer"] %}
from {{ cookiecutter.project_slug }} import cli, example_function
{%- else %}
from {{ cookiecutter.project_slug }} import example_function
{%- endif %}


def test_version() -> None:
    from {{ cookiecutter.project_slug }} import __version__

    assert __version__ != "999"


@pytest.fixture
def response() -> tuple[int, int]:
    return 1, 2


def test_example_function(response: tuple[int, int]) -> None:
    expected = 3
    assert example_function(*response) == expected
{%- if cookiecutter.command_line_interface in ["click", "typer"] %}


def test_command_line_interface() -> None:
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
