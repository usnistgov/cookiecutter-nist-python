################################################################################
# * Utilities
################################################################################
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
	match = re.match(r'^([a-zA-Z_/.-]+):.*?## (.*)$$', line)
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
	rm -fr dist-conda/


clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-nox: ## remove all nox artifacts
	rm -fr .nox

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache



################################################################################
# * Pre-commit
################################################################################
.PHONY: pre-commit-init pre-commit pre-commit-all
pre-commit-init: ## install pre-commit
	pre-commit install

pre-commit-all: ## run pre-commit on all files
	pre-commit run --all-files

pre-commit-codespell: ## run codespell. Note that this imports allowed words from docs/spelling_wordlist.txt
	pre-commit run --all-files codespell
	pre-commit run --all-files nbqa-codespell

pre-commit-typos:  ## run typos.
	pre-commit run --all-files --hook-stage manual typos
	pre-commit run --all-files --hook-stage manual nbqa-typos

################################################################################
# * User setup
################################################################################
.PHONY: user-autoenv-zsh user-all
user-autoenv-zsh: ## create .autoenv.zsh files
	echo conda activate ./.venv > .autoenv.zsh
	echo conda deactivate > .autoenv_leave.zsh

user-all: user-autoenv-zsh ## runs user scripts


################################################################################
# * Testing
################################################################################
.PHONY: test coverage
test: ## run tests quickly with the default Python
	pytest -x -v

test-accept: ## run tests and accept doctest results. (using pytest-accept)
	DOCFILLER_SUB=False pytest -v --accept

coverage: ## check code coverage quickly with the default Python
	coverage run --source cookiecutter_nist_python -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html


################################################################################
# * Versioning
################################################################################
# .PHONY: version-scm version-import version

# version-scm: ## check/update version of package with setuptools-scm
# 	python -m setuptools_scm

# version-import: ## check version from python import
# 	-python -c 'import cookiecutter_nist_python; print(cookiecutter_nist_python.__version__)'

# version: version-scm version-import

################################################################################
# * Requirements/Environment files
################################################################################
.PHONY: requirements
requirements: ## rebuild all requirements/environment files
	nox -s requirements
requirements/%.yaml: pyproject.toml
	nox -s requirements
requirements/%.txt: pyproject.toml
	nox -s requirements

################################################################################
# * NOX
###############################################################################
# NOTE: Below, we use requirement of the form "requirements/dev.txt"
# Since any of these files will trigger a rebuild of all requirements,
# the actual "txt" or "yaml" file doesn't matter
# ** dev
NOX=nox
.PHONY: dev-env
dev-env: requirements/dev.txt ## create development environment using nox
	$(NOX) -e dev

# ** testing
.PHONY: test-all
test-all: requirements/test.txt ## run tests on every Python version with nox.
	$(NOX) -s test

# ** docs
.PHONY: docs-build docs-release docs-clean
docs-build: ## build docs in isolation
	$(NOX) -s docs -- +d build
docs-clean: ## clean docs
	rm -rf docs/_build/*
	rm -rf docs/generated/*
	rm -rf docs/reference/generated/*
docs-clean-build: docs-clean docs-build ## clean and build
docs-release: ## release docs.
	$(NOX) -s docs -- +d release

.PHONY: .docs-spelling docs-nist-pages docs-open docs-livehtml docs-clean-build docs-linkcheck
docs-spelling: ## run spell check with sphinx
	$(NOX) -s docs -- +d spelling
docs-livehtml: ## use autobuild for docs
	$(NOX) -s docs -- +d livehtml
docs-open: ## open the build
	$(NOX) -s docs -- +d open
docs-linkcheck: ## check links
	$(NOX) -s docs -- +d linkcheck

docs-build docs-release docs-clean docs-livehtml docs-linkcheck: requirements/docs.txt

# ** typing
.PHONY: typing-mypy typing-pyright typing-pytype typing-all
typing-mypy: ## run mypy mypy_args=...
	$(NOX) -s typing -- +m mypy
typing-pyright: ## run pyright pyright_args=...
	$(NOX) -s typing -- +m pyright
typing-pytype: ## run pytype pytype_args=...
	$(NOX) -s typing -- +m pytype
typing-all:
	$(NOX) -s typing -- +m mypy pyright pytype
typing-mypy typing-pyright typing-pytype typing-all: requirements/typing.txt

# ** dist pypi
.PHONY: build testrelease release
build: requirements/build.txt ## build dist
	$(NOX) -s build
testrelease: ## test release on testpypi
	$(NOX) -s publish -- +p test
release: ## release to pypi, can pass posargs=...
	$(NOX) -s publish -- +p release

.PHONY: check-release check-wheel check-dist
check-release: ## run twine check on dist
	$(NOX) -s publish -- +p check
check-wheel: ## Run check-wheel-contents (requires check-wheel-contents to be installed)
	check-wheel-contents dist/*.whl
check-dist: check-release check-wheel ## Run check-release and check-wheel
.PHONY:  list-wheel list-sdist list-dist
list-wheel: ## Cat out contents of wheel
	unzip -vl dist/*.whl
list-sdist: ## Cat out contents of sdist
	tar -tzvf dist/*.tar.gz
list-dist: list-wheel list-sdist ## Cat out sdist and wheel contents

# ** dist conda
.PHONY: conda-recipe conda-build
conda-recipe: ## build conda recipe can pass posargs=...
	$(NOX) -s conda-recipe
conda-build: ## build conda recipe can pass posargs=...
	$(NOX) -s conda-build

# ** list all options
.PHONY: nox-list
nox-list:
	$(NOX) --list


################################################################################
# * Installation
################################################################################
.PHONY: install install-dev
install: ## install the package to the active Python's site-packages (run clean?)
	pip install . --no-deps

install-dev: ## install development version (run clean?)
	pip install -e . --no-deps


################################################################################
# * NOTEBOOK typing/testing
################################################################################
NOTEBOOKS ?= examples/usage
.PHONY: mypy-notebook pyright-notebook typing-notebook
mypy-notebook: ## run nbqa mypy
	nbqa --nbqa-shell mypy $(NOTEBOOKS)
pyright-notebook: ## run nbqa pyright
	nbqa --nbqa-shell pyright $(NOTEBOOKS)
typing-notebook: mypy-notebook pyright-notebook ## run nbqa mypy/pyright

.PHONY: pytest-nbval
pytest-notebook:  ## run pytest --nbval
	pytest --nbval --nbval-current-env --nbval-sanitize-with=config/nbval.ini --dist loadscope -x $(NOTEBOOKS)

.PHONY: clean-kernelspec
clean-kernelspec: ## cleanup unused kernels (assuming notebooks handled by conda environment notebook)
	conda run -n notebook python tools/clean_kernelspec.py


################################################################################
# * Other tools
################################################################################

# Note that this requires `auto-changelog`, which can be installed with pip(x)
auto-changelog: ## autogenerate changelog and print to stdout
	auto-changelog -u -r usnistgov -v unreleased --tag-prefix v --stdout --template changelog.d/templates/auto-changelog/template.jinja2

commitizen-changelog:
	cz changelog --unreleased-version unreleased --dry-run --incremental

# tuna analyze load time:
.PHONY: tuna-analyze
tuna-import: ## Analyze load time for module
	python -X importtime -c 'import cookiecutter_nist_python' 2> tuna-loadtime.log
	tuna tuna-loadtime.log
	rm tuna-loadtime.log

.PHONY: typing-tools
typing-tools:
	mypy --strict noxfile.py ./tools/*.py
	pyright noxfile.py tools/*.py

# cookiecutter stuff
BAKE_OPTIONS=--no-input

bake: ## generate project using defaults
	cookiecutter $(BAKE_OPTIONS) . --overwrite-if-exists

watch: bake ## watchmedo bake
	watchmedo shell-command -p '*.*' -c 'make bake -e BAKE_OPTIONS=$(BAKE_OPTIONS)' -W -R -D \{{cookiecutter.project_slug}}/

replay: BAKE_OPTIONS=--replay
replay: watch ## replay watch
	;

# Can't seem to convert
.PHONY: README.pdf
README.pdf: ## create README.pdf
	pandoc -V colorlinks -V geometry:margin=0.8in README.md -o README.pdf

# Cog on files:
.PHONY: cog
cog: ## run nox -s cog
	nox -s cog
