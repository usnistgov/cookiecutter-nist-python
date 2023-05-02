project_name?={{ cookiecutter.project_name }}

.PHONY: help clean-recipe clean-build recipe build command

help:
	@echo Makefile for building conda dist
clean-recipe:
	rm -rf $(project_name)

clean-build:
	rm -rf build

recipe: clean-recipe
	grayskull pypi $(project_name)     && \
	cat $(project_name)/meta.yaml

build: clean-build
	conda mambabuild --output-folder=build --no-anaconda-upload .

command:
	$(command)
