"""Console script for {{cookiecutter.project_slug}}."""

{%- if cookiecutter.command_line_interface|lower == 'argparse' %}
import argparse
{%- endif %}
import sys
{%- if cookiecutter.command_line_interface|lower == 'click' %}

import click
{%- endif %}
{%- if cookiecutter.command_line_interface|lower == 'typer' %}

import typer
{%- endif %}

PACKAGE = "{{ cookiecutter.project_slug}}"

{%- if cookiecutter.command_line_interface|lower == 'click' %}


@click.command()
def main():
    """Console script for {{cookiecutter.project_slug}}."""
    click.echo(f"Replace this message by putting your code into {PACKAGE}.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0

{%- elif cookiecutter.command_line_interface|lower == 'typer' %}

app = typer.Typer()


@app.command()
def func():
    """Console script for {{cookiecutter.project_slug}}."""
    print(f"Replace this message by putting your code into {PACKAGE}.cli.main")
    print("See click documentation at https://typer.tiangolo.com/")
    return 0


# get the click function. For use with sphinx-click
main = typer.main.get_command(app)


{%- elif cookiecutter.command_line_interface|lower == 'argparse' %}


def main():
    """Console script for {{cookiecutter.project_slug}}."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print(f"Replace this message by putting your code into {PACKAGE}.cli.main"
    return 0


{%- endif %}


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
