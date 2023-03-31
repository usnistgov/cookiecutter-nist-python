# Welcome to {{ cookiecutter.project_name }}'s documentation!

```{include} ../README.md
:end-before: <!-- end-docs -->
```

```{toctree}
:caption: 'Contents:'
:maxdepth: 1

<!-- example -->
installation
usage
notebooks/demo
api
license
contributing
{% if cookiecutter.create_author_file == 'y' -%}
authors
{% endif -%}
history
navigation
```
