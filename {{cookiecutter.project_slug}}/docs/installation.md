```{highlight} shell

```

# Installation

## Stable release

To install {{ cookiecutter.project_name }}, run this command in your terminal:

```console
$ pip install {{ cookiecutter.project_slug }}
```

or

```console
$ conda install -c {{ cookiecutter.conda_channel }} {{ cookiecutter.project_slug }}
```

This is the preferred method to install {{ cookiecutter.project_name }}, as it
will always install the most recent stable release.

If you don't have [pip] installed, this [Python installation guide] can guide
you through the process.

## From sources

The sources for {{ cookiecutter.project_name }} can be downloaded from the
[Github repo].

You can either clone the public repository:

```console
$ git clone git://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}.git
```

Once you have a copy of the source, you can install it with:

```console
$ pip install .
```

To install dependencies with conda/mamba, use:

```console

conda env create -n {name} -f environment.yaml
pip install . --no-deps
```

To install an editable version, add the `-e` option to pip.

[github repo]: https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.project_name}}
[pip]: https://pip.pypa.io
[python installation guide]:
  http://docs.python-guide.org/en/latest/starting/installation/
