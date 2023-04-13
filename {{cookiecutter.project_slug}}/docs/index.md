# Welcome to {{ cookiecutter.project_name }}'s documentation!

```{include} ../README.md
:end-before: <!-- end-docs -->
```

```{toctree}
:maxdepth: 1

<!-- example -->
installation
examples/index
reference/index
license
contributing
{% if cookiecutter.create_author_file == 'y' -%}
authors
{% endif -%}
changelog
navigation
```
