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
# Packaging and Distributing
# -----------------------------------------------------------------------------
.PHONY: build
build:
	python setup.py sdist bdist_wheel
	echo -e "\033[0;32mBuild complete"

.PHONY: clean
clean:
	rm -rf ./build ./dist ./*.egg-info
	echo "Existing distribution has been removed!"

.PHONY: build-nocache clean-and-build cab
build-nocache clean-and-build cab: clean build


###############################################################################
# Code Quality
# -----------------------------------------------------------------------------
.PHONY: black
black:
	black --version
	black --target-version py39 --line-length 99 examples lbz tests setup.py

.PHONY: black-check
black-check:
	black --version
	black --target-version py39 --line-length 99 --check examples lbz tests setup.py

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
	mypy examples lbz tests setup.py

.PHONY: pylint
pylint:
	pylint --version
	pylint examples lbz tests setup.py

.PHONY: lint
lint: flake8 mypy pylint

.PHONY: bandit
bandit:
	bandit --version
	bandit --recursive lbz setup.py

.PHONY: pip-audit
pip-audit:
	pip-audit --version
	pip-audit -r requirements.txt --ignore-vuln GHSA-wj6h-64fc-37mp

.PHONY: secure
secure: bandit pip-audit

.PHONY: format-lint-secure
format-lint-secure: format lint secure


###############################################################################
# Tests
# -----------------------------------------------------------------------------
.PHONY: test-unit tu
test-unit tu:
	coverage run --include "lbz/*" -m pytest "tests"
	coverage report -m --skip-covered

.PHONY: test-unit-verbose tuv
test-unit-verbose tuv:
	coverage run --include "lbz/*" -m pytest "tests" -vv
	coverage report -m --skip-covered

.PHONY: test
test: test-unit
