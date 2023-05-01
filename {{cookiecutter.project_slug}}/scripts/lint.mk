.PHONY: help mypy pyright pytype all

help:
	@echo Makefile for linting

posargs?=
mypy:
	-mypy --color-output $(posargs)

pyright:
	-pyright $(posargs)

pytype:
	-pytype $(posargs)

all: mypy pyright pytype

command?= @echo 'pass command=...'
command:
	$(command)
