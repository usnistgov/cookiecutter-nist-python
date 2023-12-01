<!-- markdownlint-disable MD053 -->

# Tutorial

[cookiecutter]: https://github.com/cookiecutter/cookiecutter

## Install cookiecutter

You can install [cookiecutter] in any of the following ways. It is recommended
to use [pipx] or [condax], so [cookiecutter] is centrally installed.

```bash
# using conda or mamba
conda/mamba install [-n ENVIRONMENT] cookiecutter
# using pip or pipx or condax
pip/pipx/condax install cookiecutter
```

## Generate you package

```{include} ../README.md
:start-after: <!-- start-installation -->
:end-before: <!-- end-installation -->
```

## Create a git repo

```bash
cd {my-project}
# init the project
git init
# add all files (should be used with care)
git add .
git commit -m 'a meaningful message'
```

```{include} ../CONTRIBUTING.md
:start-after: <!-- start-tutorial -->
```
