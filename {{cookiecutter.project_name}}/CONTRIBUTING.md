# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

<!-- prettier-ignore-start -->
[issues]: https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}/issues
<!-- prettier-ignore-end -->

### Report Bugs

Report bugs at [here][issues]

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation

This project could always use more documentation, whether as part of the
official docs, in docstrings, or even on the web in blog posts, articles, and
such.

### Submit Feedback

The best way to send feedback is to file an issue [here][issues].

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions are
  welcome!

## Making a contribution

Ready to contribute? Here's how to make a contribution.

- Fork the repo on GitHub.

- Clone your fork locally:

  ```bash
  git clone git@github.com:your_name_here/{{ cookiecutter.project_name }}.git
  ```

  If the repo includes submodules, you can add them either with the initial
  close using:

  ```bash
  git clone --recursive-submodules git@github.com:your_name_here/{{ cookiecutter.project_name }}.git
  ```

  or after the clone using

  ```bash
  cd {{ cookiecutter.project_name }}
  git submodule update --init --recursive
  ```

- Create development environment. See [](#bootstrap-development-environment) for
  details.

- Initiate [pre-commit] with:

  ```bash
  pre-commit install
  ```

  To update the recipe, periodically run:

  ```bash
  pre-commit autoupdate
  ```

  If recipes change over time, you can clean up old installs with:

  ```bash
  pre-commit gc
  ```

- Create a branch for local development:

  ```bash
  git checkout -b name-of-your-bugfix-or-feature
  ```

  Now you can make your changes locally. Alternatively, we recommend using
  [git-flow].

- When you're done making changes, check that your changes pass the pre-commit
  checks: tests.

  ```bash
  pre-commit run [--all-files]
  ```

  To run tests, use:

  ```bash
  pytest
  ```

  To test against multiple python versions, use [nox]:

  ```bash
  nox -s test
  ```

  Additionally, you should run the following:

  ```bash
  make pre-commit-lint-markdown
  make pre-commit-codespell
  ```

- Create changelog fragment. See [scriv] for more info.

  ```bash
  scriv create --edit
  ```

- Commit your changes and push your branch to GitHub:

  ```bash
  git add .
  git commit -m "Your detailed description of your changes."
  git push origin name-of-your-bugfix-or-feature
  ```

  Note that the pre-commit hooks will force the commit message to be in the
  [conventional style][conventional-style]. To assist this, you may want to
  commit using [commitizen].

  ```bash
  cz commit
  ```

- Submit a pull request through the GitHub website.

<!-- start-tutorial -->

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

You can also run [pre-commit] on all files via nox using:

```bash
nox -s lint
```

## Using nox

This project makes extensive use of [nox] to automate testing, typing,
documentation creation, etc. One downside of using [tox] with this particular
workflow is the need for multiple scripts/makefiles, while with [nox], most
everything is self contained in the file `noxfile.py`. [nox] also allows for a
mix of [conda] and [virtualenv] environments. The default is for the development
environment to use conda, while all other environments are virtualenvs. There
are conda sessions for testing (`test-conda`), typing (`typing-conda`), docs
(`docs-conda`), etc.

### Setup user configuration

As discussed below, we need to tell nox where to search for python interpreters
(if using virtualenvs), and what "extras" from `pyproject.toml` to include in
the users development environment. For this, create the file
`config/userconfig.toml`. An example of this file is available at
`config/userconfig.example.toml`. The variable `nox.python.paths` is a list of
paths (with optional wildcards) added to the environment variable `PATH` to
search for python interpreters. The variable `nox.extras.dev` is a list of
"extras" to include (from `pyproject.toml`) in the development environment.

```toml
# config/userconfig.toml
[nox.python]
paths = ["~/.conda/envs/python-3.*/bin"]

# overrides dev environment for user
[tool.pyproject2conda.envs.dev]
extras = ["dev", "nox"]

```

For example, the above file will add the paths `~/.conda/envs/python-3.*/bin` to
the search path, and the development environment will include the extras `dev`
and `nox` from the `project.optional-dependencies` section of the
`pyproject.toml` file in the development environment. See
[below](#creating-environmentyamlrequirementtxt-files) and [pyproject2conda] for
more info.

You can also create this file using either of the following commands:

```bash
nox -s config -- ++python-paths "~/.conda/envs/python-3.*/bin" ++dev-extras dev nox...
# or
python tools/projectconfig.py  --python-paths ... --dev-extras ...
```

Run the latter with `--help` for more options.

### Installing interpreters for virtualenv creation

If using virtualenvs across multiple python versions (e.g., `test_venv`,
`typing_venv`, etc), you'll need to install python interpreters for each
version. I've had trouble mixing pyenv with conda. Instead, I use conda to
create multiple invironments to hold different python version. You can use the
following script to create the needed conda environments:

```bash
python tools/create_pythons.py -p 3.8 3.9 ...
```

Run with `--help` for more options. Then, set the variable `nox.python.paths`
(see [](#setup-user-configuration)).

### Nox session options

To see all nox session, run:

```bash
nox --list
```

To simplify passing options to underlying commands, the options to a particular
nox session use `+` instead of `-` for options. For example, pass options to
pytest, use:

```bash
nox -s test -- ++test-opts -x -v
```

Using `+` for the session option `++test-opts` means we don't have to escape
`-x` or `-v`. To see all options:

```bash
nox -- ++help/+h
```

Note that these options should be passed _after_ `--`. For example, to build and
open the documentation, run:

```bash
nox -s docs -- +d build open
```

### Creating environment.yaml/requirement.txt files

The project is setup to create `environemt.yaml` and `requirement.txt` files
from `pyproject.toml`. This can be done using:

```bash
nox -s requirements
```

This uses [pyproject2conda] to create the requirement files. Note that all
requirement files are under something like
`requirements/py{version}-{env-name}.yaml` (conda environment) or
`requirements/{env-name}.txt` (virtual environment). The file
`requirements/py{version}-dev.yaml` is user specific and **should not** be
tracked by git.

Additionally, requirement files for virtualenvs (e.g., `requirements.txt` like
files) will be "locked" using `pip-compile`. These files are placed under
`requirements/lock`.

## ipykernel

The environments created by nox `dev` and `docs-conda` will try to add
meaningful display names for ipykernel (assuming you're using
[nb_conda_kernels])

## Building the docs

We use [nox] to isolate the documentation build. Specific tasks can be run with

```bash
nox -s docs -- +d [commands]
```

where commands can be one of:

- clean : remove old doc build
- build/html : build html documentation
- spelling : check spelling
- linkcheck : check the links
- symlink : rebuild symlinks from `examples` to `docs/examples`
- release : make pages branch for documentation hosting (using
  [ghp-import](https://github.com/c-w/ghp-import))
- livehtml : Live documentation updates
- open : open the documentation in a web browser
- serve : Serve the created documentation webpage (Need this to view javescript
  in created pages).

## Testing with nox

The basic command is:

```bash
nox -s test -- [++test-opts] [++no-cov]
```

where you can pass in additional pytest options via `++test-opts`. For example:

```bash
nox -s test -- ++test-opts -x -v
```

Use session `test-conda` to test under a conda environment.

## Building distribution for conda

[grayskull]: https://github.com/conda/grayskull

For the most part, we use [grayskull] to create the conda recipe. However, I've
had issues getting it to play nice with `pyproject.toml` for some of the 'extra'
variables. So, we use grayskull to build the majority of the recipe, and append
the file `config/recipe-append.yaml`. For some edge cases (install name
different from package name, etc), you'll need to manually edit this file to
create the final recipe.

To build the conda recipe using [grayskull]:

```bash
nox -s conda-recipe -- ++conda-recipe [recipe, recipe-full]
```

To build the conda distribution:

```bash
nox -s conda-build -- ++conda-build [build,clean]
```

To upload the recipe, you'll need to run an external command like:

```bash
nox -s conda-build -- ++conda-build-run "anaconda upload PATH-TO-TARBALL"
```

## Building distribution for pypi

The basic command is:

```bash
nox -s build
```

To upload the pypi distribution:

```bash
nox -s publish -- +p [release, test]
```

- test : upload to testpypi
- release : upload to pypi

## Testing pypi or conda installs

Run:

```bash
nox -s testdist-pypi -- ++version [version]
```

to test a specific version from pypi and

```bash
nox -s testdist-conda -- ++version [version]
```

to to likewise from conda.

## Type checking

Run:

```bash
nox -s typing -- +m [commands] [options]
```

Use `typing-conda` to test typing in a conda environment.

## Setup development environment

This project uses a host of tools to (hopefully) make development easier. We
recommend installing some of these tools system wide. For this, we recommend
using either [pipx] or [condax]. We mostly use conda/condax, but the choice is
yours. For conda, we recommend actually using [mamba]. Alternatively, you can
setup `conda` to use the faster `mamba` solver. See [here][conda-fast-setup] for
details.

### Bootstrap development environment

The recommended method to install the development environment is to use nox. The
following commands Will create the user config file `config/userconfig.toml`,
the requirements files, and the development environment.

```bash
nox -s config requirements dev -- ++python-paths ... ++dev-extras ...
```

See [](#setup-user-configuration) for more info on the flags. You can instead
just run the session `bootstrap`, which in turn calls `config`, `requirements`,
and `dev`.

To run the above, you first need [nox] installed. You can bootstrap the while
procedure using [pipx] and the following command:

```bash
pipx run --spec git+https://github.com/wpk-nist-gov/nox-bootstrap.git \
     nox -s bootstrap -- \
     ++python-paths "~/.conda/envs/python-3.*/bin" \
     ++dev-extras dev nox

conda activate .nox/{project-name}/envs/dev
```

where options `--python-paths` and `--dev-extras` are user specific. This will,
in isolation, install nox, and run the `bootstrap` session.

Note that nox environments are under `.nox/{project-name}/envs` instead of under
`.nox`. This fixes some issues with things like [nb_conda_kernels], as well as
other third party tools that expect conda environment to be located in a
directory like `.../miniforge/envs/env-name`.

If you go this route, you may want to use something like
[zsh-autoenv](https://github.com/Tarrasch/zsh-autoenv) (if using zsh shell) or
[autoenv](https://github.com/hyperupcall/autoenv) (if using bash) to auto
activate the development environment when in the parent directory.

### Conda create development environment

If instead you'd like to just install directly with conda, you can use:

```bash
conda env create [-n {env-name}] -f requirements/py{version}-dev-complete.yaml
conda activate {env-name}
pip install -e . --no-deps
```

This installs all optional dependencies except those need to build the docs. For
that, please use nox.

### Development tools

We recommend installing the following tools with [pipx] or [condax]. If you'd
like to install them in the development environment instead, include the
"extras" `tools` in the `nox.extras.dev` section of `config/userconfig.toml`
file, or run:

```bash
nox -s config -- ++dev-extras dev nox tools
```

Alternatively, you can just create a conda environment using the commands in
[](#conda-create-development-environment).

Additional tools are:

- [pre-commit]
- [nox] with [noxopt]
- [cruft]
- [scriv]
- [commitizen] (optional)
- [pyproject2conda] (optional)
- [cog] (optional)
- [nbqa] (optional)
- [pyright] (recommended)

These are setup using the following:

```console
condax/pipx install pre-commit
condax/pipx install cruft
pipx install scriv

# optional packages
condax/pipx install commitizen
condax/pipx install cogapp
condax/pipx install nbqa
condax/pipx install pyright
```

If you'd like to install a central [nox] to be used with this project, use one
of the following:

```bash
pipx install nox
pipx inject nox ruamel.yaml
pipx inject nox noxopt
```

or

```bash
condax install nox
condax inject nox ruamel.yaml
conda activate ~/.condax/nox
pip install noxopt
```

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

- The pull request should include tests.
- If the pull request adds functionality, the docs should be updated. Put your
  new functionality into a function with a docstring, and add the feature to the
  list in `CHANGELOG.md`. You should use [scriv] for this.
- The pull request should work for all supported python versions.

## Package version

[setuptools_scm]: https://github.com/pypa/setuptools_scm

Versioning is handled with [setuptools_scm]. The package version is set by the
git tag. For convenience, you can override the version with nox setting
`--version ...`. This is useful for updating the docs, etc.

Note that the version in a given environment/session can become stale. The
easiest way to update the installed package version version is to reinstall the
package. This can be done using the following:

```bash
pip install -e . --no-deps
```

To do this in a given session, use:

```bash
nox -s {session} -- +P/++update-package
```

[conda]: https://docs.conda.io/en/latest/
[virtualenv]: https://virtualenv.pypa.io/en/latest/
[pipx]: https://github.com/pypa/pipx
[condax]: https://github.com/mariusvniekerk/condax
[mamba]: https://github.com/mamba-org/mamba
[conda-fast-setup]:
  https://www.anaconda.com/blog/a-faster-conda-for-a-growing-community
[pre-commit]: https://pre-commit.com/
[nox]: https://github.com/wntrblm/nox
[noxopt]: https://github.com/rmorshea/noxopt
[tox]: https://tox.wiki/en/latest/
[cruft]: https://github.com/cruft/cruft
[cog]: https://github.com/nedbat/cog
[git-flow]: https://github.com/nvie/gitflow
[scriv]: https://github.com/nedbat/scrivl
[conventional-style]: https://www.conventionalcommits.org/en/v1.0.0/
[commitizen]: https://github.com/commitizen-tools/commitizen
[nb_conda_kernels]: https://github.com/Anaconda-Platform/nb_conda_kernels
[pyproject2conda]: https://github.com/wpk-nist-gov/pyproject2conda
[nbqa]: https://github.com/nbQA-dev/nbQA
[pyright]: https://github.com/microsoft/pyright
