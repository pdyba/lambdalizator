black:
	black . --line-length 99

test:
	coverage run --include 'tests/*' -m pytest "tests"
	coverage report --skip-covered

build:
	python setup.py sdist bdist_wheel

upload:
	python3 -m twine upload dist/*

requirements-dev:
	pip install -r requirements_dev.txt

lint:
	pylint lbz  --rcfile=.pylintrc
