# Tutorial

<!-- [NIST]: https://www.nist.gov/ -->

[cookiecutter]: https://github.com/cookiecutter/cookiecutter

<!-- [cruft]: https://cruft.github.io/cruft/ -->

[nox]: https://nox.thea.codes/en/stable/
[pre-commit]: https://pre-commit.com/

<!-- [Sphinx]: https://www.sphinx-doc.org/en/master/ -->
<!-- [MyST]: https://myst-parser.readthedocs.io/en/latest/ -->
<!-- [furo]: https://pradyunsg.me/furo/ -->
<!-- [sphinx-book-theme]: https://sphinx-book-theme.readthedocs.io/ -->
<!-- [nist-pages]: https://pages.nist.gov/pages-root/ -->
<!-- [cookiecutter-pypackage]: -->
<!--   https://github.com/audreyfeldroy/cookiecutter-pypackage/ -->

[conda]: https://docs.conda.io/en/latest/
[virtualenv]: https://virtualenv.pypa.io/en/latest/

<!-- [pyproject2conda]: https://github.com/usnistgov/pyproject2conda -->

[pipx]: https://pypa.github.io/pipx/
[condax]: https://mariusvniekerk.github.io/condax/

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

## Using [pre-commit]

It is highly recommended to enable [pre-commit]. To do so, you need to first
install pre-commit. It is recommended to use [pipx] or [condax]

```bash
pipx/condax install pre-commit
```

Alternatively, you can install with your development environment.

Then "install" the hooks with

```bash
pre-commit install
```

This will enable a variety of code-checkers (linters) when you add a file to
commit. Alternatively, you can run the hooks over all files using:

```bash
pre-commit run --all-files
```

## Using [nox]

The project is setup to use [nox] to run tests, build documentation, and run
checkers in isolated virtual environments. One feature of [nox] is the ability
to mix both [conda] and [virtualenv] based environments.

```{include} ../CONTRIBUTING.md
:start-after: <!-- start-tutorial -->
:end-before: <!-- end-tutorial -->
```
