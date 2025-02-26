<!-- markdownlint-disable MD041 -->

[![Repo][repo-badge]][repo-link] [![Docs][docs-badge]][docs-link]
[![PyPI license][license-badge]][license-link]
[![PyPI version][pypi-badge]][pypi-link]
[![Conda (channel only)][conda-badge]][conda-link]
[![Code style: ruff][ruff-badge]][ruff-link][![uv][uv-badge]][uv-link]

<!--
  For more badges, see
  https://shields.io/category/other
  https://naereen.github.io/badges/
  [pypi-badge]: https://badge.fury.io/py/{{ cookiecutter.project_name }}
-->

<!-- prettier-ignore-start -->
[ruff-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[ruff-link]: https://github.com/astral-sh/ruff
[uv-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json
[uv-link]: https://github.com/astral-sh/uv
[pypi-badge]: https://img.shields.io/pypi/v/{{ cookiecutter.project_name }}
[pypi-link]: https://pypi.org/project/{{ cookiecutter.project_name }}
[docs-badge]: https://img.shields.io/badge/docs-sphinx-informational
[docs-link]: https://pages.nist.gov/{{ cookiecutter.project_name }}/
[repo-badge]: https://img.shields.io/badge/--181717?logo=github&logoColor=ffffff
[repo-link]: https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}
[conda-badge]: https://img.shields.io/conda/v/{{ cookiecutter.conda_channel }}/{{ cookiecutter.project_name }}
[conda-link]: https://anaconda.org/{{ cookiecutter.conda_channel }}/{{ cookiecutter.project_name }}
[license-badge]: https://img.shields.io/pypi/l/cmomy?color=informational
[license-link]: https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}/blob/main/LICENSE
<!-- prettier-ignore-end -->

<!-- other links -->

# `{{ cookiecutter.project_name }}`

A Python package for stuff.

## Overview

Quick overview...

## Features

Some features...

## Status

This package is actively used by the author. Please feel free to create a pull
request for wanted features and suggestions!

## Quick start

Use one of the following

```bash
pip install {{ cookiecutter.project_name }}
```

or

```bash
conda install -c {{ cookiecutter.conda_channel}} {{ cookiecutter.project_name }}
```

## Example usage

```python
import {{ cookiecutter.project_slug }}
```

<!-- end-docs -->

## Documentation

See the [documentation][docs-link] for further details.

## License

This is free software. See [LICENSE][license-link].

## Related work

Any other stuff to mention....

## Contact

The author can be reached at <{{ cookiecutter.email }}>.

## Credits

This package was created using
[Cookiecutter](https://github.com/audreyr/cookiecutter) with the
[usnistgov/cookiecutter-nist-python](https://github.com/usnistgov/cookiecutter-nist-python)
template.
