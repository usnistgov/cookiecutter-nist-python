# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at <https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/issues>.

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

{{ cookiecutter.project_name }} could always use more documentation, whether as part of the
official {{ cookiecutter.project_name }} docs, in docstrings, or even on the web in blog posts,
articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at <https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/issues>.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Get Started!


### Environment setup

[pipx]: https://github.com/pypa/pipx
[condax]: https://github.com/mariusvniekerk/condax
[mamba]: https://github.com/mamba-org/mamba
[conda-fast-setup]: https://www.anaconda.com/blog/a-faster-conda-for-a-growing-community
[pre-commit]: https://pre-commit.com/
[tox]: https://tox.wiki/en/latest/
[tox-conda]: https://github.com/tox-dev/tox-conda
[cruft]: https://github.com/cruft/cruft
[conda-merge]: https://github.com/amitbeka/conda-merge
[git-flow]: https://github.com/nvie/gitflow

This project uses a host of tools to (hopefully) make development easier.  We recommend installing some of these tools system wide.  For this, we recommend using
either [pipx] or [condax].  We mostly use conda/condax, but the choice is yours.  For conda, we recommend actually using [mamba]. Alternatively, you can setup `conda` to use the faster `mamba` solver.
See [here][conda-fast-setup] for details.

Additional dependencies are:

* [pre-commit]
* [tox] and [tox-conda]
* [cruft]
* [conda-merge]

These are setup using the following:

```bash
condax install pre-commit
condax install tox
condax inject tox tox-conda
condax install cruft
condax install conda-merge
```

### Getting the repo

Ready to contribute? Here's how to set up `{{ cookiecutter.project_slug }}` for local development.

1. Fork the `{{ cookiecutter.project_slug }}` repo on GitHub.

2. Clone your fork locally:

    ```bash
    git clone git@github.com:your_name_here/{{ cookiecutter.project_slug }}.git
    ```

3. Create development environment.  Using the makefile will install a development version using mamba.

    ```bash
    make mamba-dev
    ```

4. Initiate pre-commit with:

    ```bash
    pre-commit init
    ```

    To update the recipe, periodically run:

    ```bash
    pre-commit autoupdate
    ```

5. Install editable package:

    ```bash
    pip install -e . --no-deps
    ```

    or

    ```bash
    make install-dev
    ```

07. Create a branch for local development:

    ```bash
    git checkout -b name-of-your-bugfix-or-feature
    ```

    Now you can make your changes locally.  Alternatively, we recommend using [git-flow].

08. When you're done making changes, check that your changes pass the pre-commit checks:
    tests.

    ```bash
    pre-commit run [--all-files]
    ```

    To run tests, use:

    ```bash
    pytest
    ```

    To test against multiple python versions, use tox:

    ```bash
    tox
    ```

    or using the makefile:

    ```bash
    make test-all
    ```


09. Commit your changes and push your branch to GitHub:

    ```
    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature
    ```

10. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.8, 3.9, 3.10.

## Building the docs

We use [tox] to isolate the documentaion build.  Useful commands are as follows.

* Build the docs:

    ```bash
    tox -e docs-build
    ```

* Spellcheck the docs:

    ```bash
    tox -e docs-spelling
    ```

* Create a relese of the docs:

    ```bash
    tox -e docs-release
    ```

    After this, the docs can be pushed to the correct branch for distribution.

* Live documentation updates using

## Using tox

The package is setup to use tox to test, build and release pip and conda distributions, and release the docs.  Most of these tasks have a command in the makefie.  To test against multiple versions, use:

```
$ make test-all
```

To build the documentation in an isolated environment, use:

```
$ make docs-build
```

To release the documentation use:

```
$ make docs-release posargs='-m "commit message" -r origin -p'
```

Where posargs is are passed to ghp-import.  Note that the branch created is called `nist-pages`.  This can be changed in `tox.ini`.

To build the distribution, use:

```
$ make dist-pypi-[build-testrelease-release]
```

where `build` build to distro, `testrelease` tests putting on `testpypi` and release puts the distro on pypi.

To build the conda distribution, use:

```
$ make dist-conda-[recipe, build]
```

where `recipe` makes the conda recipe (using grayskull), and `build` makes the distro.  This can be manually added to a channel.

To test the created distributions, you can use one of:

```
$ make test-dist-[pypi, conda]-[local,remote] py=[38, 39, 310]
```
