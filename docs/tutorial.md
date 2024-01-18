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

## Using setuptools instead of hatchling

[hatchling]: https://github.com/pypa/hatch/tree/master/backend
[setuptools]: https://github.com/pypa/setuptools

The repo by default uses [hatchling] for building the package. I've found that
[setuptools] is overkill for python only projects. However, if you'd like to use
[setuptools] (if, for example, your package includes non-python code), you can
use something like the following:

```toml
# pyproject.toml
[build-system]
build-backend = "setuptools.build_meta"
requires = [
    "setuptools>=61.2",
    "setuptools_scm[toml]>=8.0",
]

...

[tool.setuptools]
zip-safe = true # if using mypy, must be False
include-package-data = true
license-files = ["LICENSE"]

[tool.setuptools.packages.find]
namespaces = true
where = ["src"]

[tool.setuptools.dynamic]
readme = { file = [
    "README.md",
    "CHANGELOG.md",
    "LICENSE"
], content-type = "text/markdown" }

[tool.setuptools_scm]
fallback_version = "999"
```

Also remove the sections `tool.hatch.version` and
`tool.hatch.metadata.hooks.fancy-pypi-readme`. You may have to add the file
`MANIFEST.in` to include/exclude files if needed.
