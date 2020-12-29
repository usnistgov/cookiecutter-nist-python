.PHONY: clean clean-test clean-pyc clean-build docs help
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

lint: ## check style with flake8
	flake8 {{ cookiecutter.project_slug }} tests


pre-commit-init: ## install pre-commit
	pre-commit install

pre-commit-run: ## run pre-commit
	pre-commit run

pre-commit-run-all: ## run pre-commit on all files
	pre-commit run --all-files

versioneer-init: ## install versioneer
	versioneer install

init: pre-commit-init versioneer-init ## run pre-commit and versioneer init

conda-env: ## conda create base env
	conda env create -f environment.yml

conda-dev: ## conda update development dependencies
	conda env update -n {{ cookiecutter.project_slug }}-env -f environment-dev.yml

conda-all: conda-create-env conda-create-dev ## conda create development env

mamba-env: ## mamba create base env
	mamba env create -f environment.yml

mamba-dev: ## mamba update development dependencies
	mamba env update -n {{ cookiecutter.project_slug }}-env -f environment-dev.yml

mamba-all: mamba-create-env mamba-create-dev ## mamba create development env

activate: ## activate base env
	conda activate {{ cookiecutter.project_slug }}-env

user-venv: ## create .venv file with name of conda env
	echo {{ cookiecutter.project_slug}}-env > .venv

user-autoenv-zsh: ## create .autoenv.zsh files
	echo conda activate {{ cookiecutter.project_slug}}-env > .autoenv.zsh
	echo conda deactivate > .autoenv_leave.zsh

user-all: user-venv user-autoenv-zsh ## runs user scripts

test: ## run tests quickly with the default Python
	pytest -x -v

test-all: ## run tests on every Python version with tox
	tox -- -x -v

coverage: ## check code coverage quickly with the default Python
	coverage run --source {{ cookiecutter.project_slug }} -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/{{ cookiecutter.project_slug }}.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ {{ cookiecutter.project_slug }}
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

release-test: dist ## package and upload to test
	twine upload --repository testpypi dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist


conda-dist:
	mkdir conda_dist; \
	cd cond_dist; \
	grayskull pypi {{ cookiecutter.project_slug }} ; \
	conda-build ; \
	echo 'upload now'

install: clean ## install the package to the active Python's site-packages
	python setup.py install

install-dev: ## install development version
	pip install -e . --no-deps
