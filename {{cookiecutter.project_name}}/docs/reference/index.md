# API Reference

```{eval-rst}
.. currentmodule:: {{ cookiecutter.project_slug }}

.. autosummary::
   :toctree: generated/

   example_function
```
{%- if cookiecutter.command_line_interface == "click" %}

```{eval-rst}

.. click:: {{ cookiecutter.project_slug }}.cli:main
    :prog: {{ cookiecutter.project_slug }}
    :nested: full
```


{%- elif cookiecutter.command_line_interface == "typer" %}

```{eval-rst}
.. typer:: {{ cookiecutter.project_slug }}.cli:main
    :prog: {{ cookiecutter.project_slug }}
    :width: 80
    :show-nested:
    :make-sections:
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
