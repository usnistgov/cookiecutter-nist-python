package_name?={{ cookiecutter.project_name }}

.PHONY: help clean recipe build command

help:
	@echo Makefile for building conda dist
clean:
	find . -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +

recipe: clean
	grayskull pypi $(package_name)     && \
	cat $(package_name)/meta.yaml

build:
	conda mambabuild --output-folder=build --no-anaconda-upload .

command:
	$(command)
