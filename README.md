<!-- markdownlint-disable MD041 -->

<!-- prettier-ignore-start -->
[![Repo][repo-badge]][repo-link]
[![Docs][docs-badge]][docs-link]
[![PyPI license][license-badge]][license-link]
[![Code style: ruff][ruff-badge]][ruff-link]
[![uv][uv-badge]][uv-link]

<!--
  For more badges, see
  https://shields.io/category/other
  https://naereen.github.io/badges/
  [pypi-badge]: https://badge.fury.io/py/cookiecutter-nist-python
-->

[ruff-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[ruff-link]: https://github.com/astral-sh/ruff
[uv-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json
[uv-link]: https://github.com/astral-sh/uv
[docs-badge]: https://img.shields.io/badge/docs-sphinx-informational
[docs-link]: https://pages.nist.gov/cookiecutter-nist-python/
[repo-badge]: https://img.shields.io/badge/--181717?logo=github&logoColor=ffffff
[repo-link]: https://github.com/usnistgov/cookiecutter-nist-python
[license-badge]: https://img.shields.io/pypi/l/cmomy?color=informational
[license-link]: https://github.com/usnistgov/cookiecutter-nist-python/blob/main/LICENSE

<!-- other links -->

[NIST]: https://www.nist.gov/
[cookiecutter]: https://github.com/cookiecutter/cookiecutter
[cruft]: https://cruft.github.io/cruft/
[nox]: https://nox.thea.codes/en/stable/
[pre-commit]: https://pre-commit.com/
[Sphinx]: https://www.sphinx-doc.org/en/master/
[MyST]: https://myst-parser.readthedocs.io/en/latest/
[furo]: https://pradyunsg.me/furo/
[sphinx-book-theme]: https://sphinx-book-theme.readthedocs.io/
[nist-pages]: https://pages.nist.gov/pages-root/
[cookiecutter-pypackage]:  https://github.com/audreyfeldroy/cookiecutter-pypackage/
[conda]: https://docs.conda.io/en/latest/
[virtualenv]: https://virtualenv.pypa.io/en/latest/
[pyproject2conda]: https://github.com/usnistgov/pyproject2conda

<!-- prettier-ignore-end -->

# `cookiecutter-nist-python`

[Cookiecutter][cookiecutter] template for python packages at [NIST].

## Overview

This template includes all [NIST] specific branding for creating a python
package.

## Features

- Testing with pytest
- Isolated testing, documentation building, etc, with [nox]
- Linting with [pre-commit]
- Documentation with [Sphinx], [MyST], using either the [furo] or
  [sphinx-book-theme] theme.
- Simple commands to upload package to [pypi], or a personal conda channel.
- Simple commands to release documentation to [nist-pages]
- Works with both [conda] and [virtualenv] based environments.
- Handle creation of `requirements.txt` and `environment.yaml` files with
  [pyproject2conda]

## Status

This package is actively used by the author. Please feel free to create a pull
request for wanted features and suggestions!

## Quick start

<!-- start-installation -->

To generate a package using [cookiecutter], run:

```bash
cookiecutter [--checkout BRANCH-NAME] https://github.com/usnistgov/cookiecutter-nist-python.git
```

where the optional argument in brackets can be used to specify a specific
branch.

Alternatively (and highly recommended) is to use [cruft]. This allows for the
template files to be updated as the template is updated. For this, you can run:

```bash
cruft create [--checkout BRANCH-NAME] https://github.com/usnistgov/cookiecutter-nist-python.git
```

<!-- end-installation -->
<!-- end-docs -->

## Documentation

See the [documentation][docs-link] for a look at `cookiecutter-nist-python` in
action.

## License

This is free software. See [LICENSE][license-link].

## Related work

The following packages use this template:

- [`cmomy`](https://github.com/usnistgov/cmomy)
- [`thermoextrap`](https://github.com/usnistgov/thermoextrap)
- [`tmmc-lnpy`](https://github.com/usnistgov/tmmc-lnpy)
- [`module-utilities`](https://github.com/usnistgov/module-utilities)
- [`analphipy`](https://github.com/conda-forge/analphipy-feedstock)
- [`pyproject2conda`](https://github.com/usnistgov/pyproject2conda)

## Other useful templates

- [cookiecutter-pypackage]. The template on which this work is based.
- [cookiecutter-hypermodern-python](https://github.com/cjolowicz/cookiecutter-hypermodern-python)

## Contact

The author can be reached at <wpk@nist.gov>.

## Credits

This template started as a fork of [cookiecutter-pypackage].

## TODO

- [ ] Github actions/automation
