.PHONY: clean clean-test clean-pyc clean-build help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr docs/_build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache




################################################################################
# utilities
################################################################################
.PHONY: lint pre-commit-init pre-commit-run pre-commit-run-all pre-commit-lint-extra pre-commit-codespell pre-commit-run-all-ruff

lint: ## check style with flake8
	flake8 cmomy tests

pre-commit-init: ## install pre-commit
	pre-commit install

pre-commit-run: ## run pre-commit
	pre-commit run

pre-commit-run-all: ## run pre-commit on all files
	pre-commit run --all-files

pre-commit-run-all-ruff: ## run ruff on on all files
	pre-commit run --all-files ruff

pre-commit-manual: ## run pre-commit manual flags
	pre-commit run --hook-stage manual

pre-commit-lint-extra: ## run all linting
	pre-commit run --all-files --hook-stage manual isort
	pre-commit run --all-files --hook-stage manual flake8
	pre-commit run --all-files --hook-stage manual pyupgrade

pre-commit-mypy: ## run mypy
	pre-commit run --all-files --hook-stage manual mypy

pre-commit-codespell: ## run codespell. Note that this imports allowed words from docs/spelling_wordlist.txt
	pre-commit run --all-files --hook-stage manual codespell

.git: ## init git
	git init

init: .git pre-commit-init ## run git-init pre-commit


################################################################################
# my convenience functions
################################################################################
.PHONY: user-venv user-autoenv-zsh user-all
user-venv: ## create .venv file with name of conda env
	echo {{ cookiecutter.project_slug }}-env > .venv

user-autoenv-zsh: ## create .autoenv.zsh files
	echo conda activate $$(cat .venv) > .autoenv.zsh
	echo conda deactivate > .autoenv_leave.zsh

user-all: user-venv user-autoenv-zsh ## runs user scripts


################################################################################
# Testing
################################################################################
.PHONY: test coverage
test: ## run tests quickly with the default Python
	pytest -x -v

coverage: ## check code coverage quickly with the default Python
	coverage run --source {{ cookiecutter.project_slug }} -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html


################################################################################
# versioning
################################################################################
.PHONY: version-scm version-import version
version-scm: ## check version of package
	python -m setuptools_scm

version-import: ## check version from python import
	python -c 'import {{ cookiecutter.project_slug }}; print({{ cookiecutter.project_slug }}.__version__)'

version: version-scm version-import

################################################################################
# Environment files
################################################################################

environment/dev.yaml: environment.yaml environment/dev-extras.yaml ## build development yaml file
	conda-merge $^ > $@

environment/docs.yaml: environment.yaml environment/docs-extras.yaml ## build docs yaml file
	conda-merge $^ > $@

environment/test.yaml: environment.yaml environment/test-extras.yaml ## build test yaml file
	conda-merge $^ > $@

.PHONY: environment-files

environment-files: environment/dev.yaml environment/docs.yaml environment/test.yaml ## rebuild all environment files


################################################################################
# virtual env
################################################################################
.PHONY: mamba-env mamba-dev mamba-env-update mamba-dev-update

mamba-env: environment.yaml ## create base environment
	mamba env create -f $<

mamba-env-update: environment.yaml ## update base environment
	mamba env update -f $<

mamba-dev: environment/dev.yaml ## create development environment
	mamba env create -f $<

mamba-dev-update: environment/dev.yaml ## update development environment
	mamba env update -f $<

################################################################################
# TOX
###############################################################################
tox_posargs?=-v
TOX=CONDA_EXE=mamba tox $(tox_posargs)

## testing

.PHONY: test-all
test-all: environment/test.yaml ## run tests on every Python version with tox
	$(TOX) -- $(posargs)


## docs
.PHONY: docs-build docs-release docs-clean docs-spelling docs-nist-pages docs-open docs-live docs-clean-build docs-linkcheck
posargs=
docs-build: ## build docs in isolation
	$(TOX) -e $@ -- $(posargs)
docs-clean: ## clean docs
	rm -rf docs/_build/*
	rm -rf docs/generated/*
	rm -rf docs/reference/generated/*
docs-clean-build: docs-clean docs-build ## clean and build
docs-release: ## release docs.  use posargs=... to override stuff
	$(TOX) -e $@ -- $(posargs)
docs-spelling: ## run spell check with sphinx
	$(TOX) -e $@ -- $(posargs)
docs-nist-pages: ## do both build and releas
	$(TOX) -e $@ -- $(posargs)
docs-live: ## use autobuild for docs
	$(TOX) -e $@ -- $(posargs)
docs-open: ## open the build
	$(BROWSER) docs/_build/html/index.html
docs-linkcheck: ## check links
	$(TOX) -e docs-build -- linkcheck

docs-build docs-release docs-clean docs-spelling docs-nist-pages docs-live: environment/docs.yaml


## distribution
.PHONY: dist-pypi-build dist-pypi-testrelease dist-pypi-release dist-conda-recipe dist-conda-build

posargs=
dist-pypi-build: ## build dist, can pass posargs=... and tox_posargs=...
	$(TOX) -e $@ -- $(posargs)
dist-pypi-testrelease: ## test release on testpypi. can pass posargs=... and tox_posargs=...
	$(TOX) -e $@ -- $(posargs)
dist-pypi-release: ## release to pypi, can pass posargs=...
	$(TOX) -e $@ -- $(posargs)
dist-pypi-build dist-pypi-testrelease dist-pypi-release: environment/dist-pypi.yaml

dist-conda-recipe: ## build conda recipe can pass posargs=...
	$(TOX) -e $@ -- $(posargs)
dist-conda-build: ## build conda recipe can pass posargs=...
	$(TOX) -e $@ -- $(pasargs)
dist-conda-build dist-conda-recipe: environment/dist-conda.yaml


## test distribution
.PHONY: test-dist-pypi-remote test-dist-conda-remote test-dist-pypi-local test-dist-conda-local

py?=310
test-dist-pypi-remote: ## test pypi install, can run as `make test-dist-pypi-remote py=39` to run test-dist-pypi-local-py39
	$(TOX) -e $@-py$(py) -- $(posargs)

test-dist-conda-remote: ## test conda install, can run as `make test-dist-conda-remote py=39` to run test-dist-conda-local-py39
	$(TOX) -e $@-py$(py) -- $(poasargs)

test-dist-pypi-local: ## test pypi install, can run as `make test-dist-pypi-local py=39` to run test-dist-pypi-local-py39
	$(TOX) -e $@-py$(py) -- $(posargs)

test-dist-conda-local: ## test conda install, can run as `make test-dist-conda-local py=39` to run test-dist-conda-local-py39
	$(TOX) -e $@-py$(py) -- $(poasargs)


test-dist-pypi: environment/test.


## list all options
.PHONY: tox-list

tox-list:
	$(TOX) -a


################################################################################
# installation
################################################################################
.PHONY: install install-dev
install: ## install the package to the active Python's site-packages (run clean?)
	pip install . --no-deps

install-dev: ## install development version (run clean?)
	pip install -e . --no-deps


################################################################################
# other tools
################################################################################

# Note that this requires `auto-changelog`, which can be installed with pip(x)
auto-changelog: ## autogenerate changelog and print to stdout
	auto-changelog -u -r usnistgov -v unreleased --tag-prefix v --stdout --template changelog.d/auto-changelog/template.jinja2

commitizen-changelog:
	cz changelog --unreleased-version unreleased --dry-run --incremental
