# API Reference

```{eval-rst}
.. currentmodule:: {{ cookiecutter.project_slug }}

.. autosummary::
   :toctree: generated/

   example_function
```
{%- if cookiecutter.command_line_interface in ["click", "typer"] %}

```{eval-rst}

.. click:: {{ cookiecutter.project_slug }}.cli:main
    :prog: {{ cookiecutter.project_slug }}
    :nested: full
```

{%- elif cookiecutter.command_line_interface == "argparse" %}

```{eval-rst}

.. argparse::
   :module: {{ cookiecutter.project_slug }}.cli
   :func: get_parser
   :prog: {{ cookiecutter.project_slug }}
   :nodefault:
```

{%- endif %}
