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
.PHONY: lint pre-commit-init pre-commit-run pre-commit-run-all init

lint: ## check style with flake8
	flake8 {{ cookiecutter.project_slug }} tests

pre-commit-init: ## install pre-commit
	pre-commit install

pre-commit-run: ## run pre-commit
	pre-commit run

pre-commit-autoupdate: ## run to update hooks
	pre-commit autoupdate


pre-commit-run-all: ## run pre-commit on all files
	pre-commit run --all-files

.git: ## init git
	git init

init: .git pre-commit-init ## run git-init pre-commit


################################################################################
# virtual env
################################################################################
.PHONY: mamba-env mamba-dev mamba-env-update mamba-dev-update activate

environment-dev.yaml: environment.yaml environment-tools.yaml
	conda-merge environment.yaml environment-tools.yaml > environment-dev.yaml

mamba-env: environment.yaml
	mamba env create -f environment.yaml

mamba-dev: environment-dev.yaml
	mamba env create -f environment-dev.yaml

mamba-env-update: environment.yaml
	mamba env update -f environment.yml

mamba-dev-update: environment-dev.yaml
	mamba env update -f environment-dev.yml

activate: ## activate base env
	conda activate {{ cookiecutter.project_slug }}-env


################################################################################
# my convenience functions
################################################################################
.PHONY: user-venv user-autoenv-zsh user-all
user-venv: ## create .venv file with name of conda env
	echo {{ cookiecutter.project_slug}}-env > .venv

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
# Docs
################################################################################
# .PHONY: docs serverdocs doc-spelling
# docs: ## generate Sphinx HTML documentation, including API docs
# 	rm -fr docs/generated
# 	$(MAKE) -C docs clean
# 	$(MAKE) -C docs html
# 	$(BROWSER) docs/_build/html/index.html

# servedocs: docs ## compile the docs watching for changes
# 	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

# docs-spelling:
# 	sphinx-build -b spelling docs docs/_build

################################################################################
# TOX
###############################################################################
tox_posargs?=-v
TOX=CONDA_EXE=mamba tox $(tox_posargs)

## testing
.PHONY: test-all
test-all: ## run tests on every Python version with tox
	$(TOX) -- $(posargs)


## docs
.PHONY: docs-build docs-release docs-nist-pages
posargs=
docs-build: ## build docs in isolation
	$(TOX) -e docs-build -- $(posargs)
docs-release: ## release docs.  use posargs=... to override stuff
	$(TOX) -e docs-release -- $(posargs)
docs-spelling:
	$(TOX) -e docs-spelling -- $(posargs)
docs-nist-pages: ## do both build and releas
	$(TOX) -e docs-build,docs-release -- $(posargs)


## distribution
.PHONY: dist-pypi-build dist-pypi-testrelease dist-pypi-release dist-conda-recipe dist-conda-build


dist-pypi-build: ## build dist, can pass posargs=... and tox_posargs=...
	$(TOX) -e $@ -- $(posargs)

dist-pypi-testrelease: ## test release on testpypi. can pass posargs=... and tox_posargs=...
	$(TOX) -e $@ -- $(posargs)

dist-pypi-release: ## release to pypi, can pass posargs=...
	$(TOX) -e $@ -- $(posargs)

dist-conda-recipe: ## build conda recipe can pass posargs=...
	$(TOX) -e $@ -- $(posargs)

dist-conda-build: ## build conda recipe can pass posargs=...
	$(TOX) -e $@ -- $(pasargs)


## test distribution
.PHONY: test-dist-pypi-remote test-dist-conda-remote test-dist-pypi-local test-dist-conda-local

py?=39
test-dist-pypi-remote: ## test pypi install, can run as `make test-dist-pypi-remote py=39` to run test-dist-pypi-local-py39
	$(TOX) -e $@-py$(py) -- $(posargs)

test-dist-conda-remote: ## test conda install, can run as `make test-dist-conda-remote py=39` to run test-dist-conda-local-py39
	$(TOX) -e $@-py$(py) -- $(poasargs)

test-dist-pypi-local: ## test pypi install, can run as `make test-dist-pypi-local py=39` to run test-dist-pypi-local-py39
	$(TOX) -e $@-py$(py) -- $(posargs)

test-dist-conda-local: ## test conda install, can run as `make test-dist-conda-local py=39` to run test-dist-conda-local-py39
	$(TOX) -e $@-py$(py) -- $(poasargs)





################################################################################
# installation
################################################################################
.PHONY: install install-dev
install: ## install the package to the active Python's site-packages (run clean?)
	pip install . --no-deps

install-dev: ## install development version (run clean?)
	pip install -e . --no-deps
