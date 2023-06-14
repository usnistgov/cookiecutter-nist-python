# Installation

## Stable release

To install {{ cookiecutter.project_name }}, run this command in your terminal:

```bash
pip install {{ cookiecutter.project_name }}
```

or

```bash
conda install -c {{ cookiecutter.conda_channel }} {{ cookiecutter.project_name }}
```

This is the preferred method to install {{ cookiecutter.project_name }}, as it
will always install the most recent stable release.

## From sources

The sources for {{ cookiecutter.project_name }} can be downloaded from the
[Github repo].

You can either clone the public repository:

```bash
git clone git://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}.git
```

Once you have a copy of the source, you can install it with:

```bash
pip install .
```

To install dependencies with conda/mamba, use:

```bash
conda env create [-n {name}] -f environment/base.yaml
conda activate {name}
pip install [-e] --no-deps .
```

If `environment/base.yaml` does not exist, it can be generated with:

```bash
pip/pipx install pyproject2conda
pyproject2conda yaml -o environment/base.yaml
```

where options in brackets are options (for environment name, and editable
install, repectively).

[github repo]: https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.project_name}}
