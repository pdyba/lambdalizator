SHELL = /bin/bash

.SILENT:


###############################################################################
# Python Requirements
# -----------------------------------------------------------------------------
.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: install-dev
install-dev:
	pip install -r requirements.txt -r requirements-dev.txt

.PHONY: lock-dependencies
lock-dependencies:
	pip-compile
	pip-compile requirements-dev.in

.PHONY: upgrade-dev
upgrade-dev:
	pip-compile --upgrade requirements-dev.in

.PHONY: upgrade-all
upgrade-all:
	pip-compile --upgrade
	pip-compile --upgrade requirements-dev.in


###############################################################################
# Code Quality
# -----------------------------------------------------------------------------
.PHONY: black
black:
	black --version
	black --target-version py38 --line-length 99 examples lbz tests setup.py

.PHONY: black-check
black-check:
	black --version
	black --target-version py38 --line-length 99 --check examples lbz tests setup.py

.PHONY: isort
isort:
	isort --version-number
	isort examples lbz tests setup.py

.PHONY: isort-check
isort-check:
	isort --version-number
	isort --check-only examples lbz tests setup.py

.PHONY: format
format: black isort

.PHONY: flake8
flake8:
	flake8 --version
	flake8 examples lbz tests setup.py

.PHONY: mypy
mypy:
	mypy --version
	mypy lbz tests/test_events setup.py  # TODO: start validating the rest of the code by mypy

.PHONY: pylint
pylint:
	pylint --version
	pylint examples lbz tests setup.py

.PHONY: lint
lint:  flake8 mypy pylint

.PHONY: format-and-lint
format-and-lint: format lint


###############################################################################
# Tests
# -----------------------------------------------------------------------------
.PHONY: test-unit tu
test-unit tu:
	coverage run --include "lbz/*" -m pytest "tests"
	coverage report -m --skip-covered

.PHONY: test
test: test-unit

.PHONY: test-unit-verbose tuv
test-unit-verbose tuv:
	coverage run --include "lbz/*" -m pytest "tests" -vv
	coverage report -m --skip-covered

###############################################################################
# Custom Scripts
# -----------------------------------------------------------------------------
.PHONY: build
build:
	python setup.py sdist bdist_wheel

.PHONY: upload
upload:
	python3 -m twine upload dist/*
