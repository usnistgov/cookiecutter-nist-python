# API Reference

```{eval-rst}
.. currentmodule:: {{ cookiecutter.project_slug }}

.. autosummary::
   :toctree: generated/

   example_function
```
{%- if cookiecutter.command_line_interface|lower in ["click", "typer"] %}

```{eval-rst}

.. click:: {{ cookiecutter.project_slug }}.cli:main
    :prog: {{ cookiecutter.project_slug }}
    :nested: full
```
{%- endif %}
