black:
	black . --line-length 99

black-check:
	black . --line-length 99 --check

test:
	coverage run --include 'lbz/*' -m pytest "tests"
	coverage report --skip-covered -m

build:
	python setup.py sdist bdist_wheel

upload:
	python3 -m twine upload dist/*

requirements-dev:
	pip install -r requirements_dev.txt

lint:
	pylint setup.py lbz examples tests
	mypy setup.py lbz # examples tests
	flake8 setup.py lbz examples tests
