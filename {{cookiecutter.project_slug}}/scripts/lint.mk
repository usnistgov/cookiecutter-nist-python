.PHONY: help mypy pyright pytype all

help:
	@echo Makefile for linting

mypy:
	-mypy --color-output $(mypy-args)

pyright:
	-pyright $(pyright-args)

pytype:
	-pytype $(pytype-args)

all: mypy pyright pytype

command?= @echo 'pass command=...'
command:
	$(command)
