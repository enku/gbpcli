.SHELL := /bin/bash
.DEFAULT_GOAL := gbp
PYTHON := python3.10

name := $(shell pdm show --name)
version := $(shell pdm show --version)
sdist := dist/$(name)-$(version).tar.gz
venv := .venv/pyenv.cfg
wheel := dist/$(subst -,_,$(name))-$(version)-py3-none-any.whl
src := $(shell find src -type f -print)
tests := $(shell find tests -type f -print)


.coverage: $(venv) $(src) $(tests)
	pdm run coverage run -m unittest discover --failfast

.PHONY: test
test: .coverage

coverage-report: .coverage
	pdm run coverage html
	pdm run python -m webbrowser -t file://$(CURDIR)/htmlcov/index.html

gbp:
	pdm run shiv --compressed -o $@ -e gbpcli:main .


build: $(sdist) $(wheel)

.PHONY: wheel
wheel: $(wheel)

.PHONY: sdist
sdist: $(sdist)

$(sdist) $(wheel): $(src) $(venv)
	pdm build

$(venv):
	rm -rf .venv
	pdm sync --dev
	touch $@

.PHONY: clean
clean: clean-build clean-venv
	rm -rf .coverage gbp htmlcov .mypy_cache

.PHONY: clean-build
clean-build:
	rm -rf dist build

.PHONY: clean-venv
clean-venv:
	rm -rf .venv

.PHONY: shell
shell: $(venv)
	bash -l

.PHONY: lint
lint: $(venv)
	pdm run pylint src tests
	pdm run mypy src

.PHONY: fmt
fmt:
	pdm run isort src tests
	pdm run black src tests
