black:
	black . --line-length 99

black-check:
	black . --line-length 99 --check

test:
	coverage run --include 'lbz/*' -m pytest "tests"
	coverage report --skip-covered -m

real-coverage:
	for file in $$(find lbz -type f \( -name "*.py" -and ! -name "*_.py" \)); do       \
		atest="test$${file/lbz\//_}"; \
		echo $$file; \
		echo "tests/$${atest/\//_}"; \
		coverage run --include $$file -m pytest "tests/$${atest/\//_}"; \
		coverage report --skip-covered -m; \
	done

build:
	python setup.py sdist bdist_wheel

upload:
	python3 -m twine upload dist/*

requirements-dev:
	pip install -r requirements_dev.txt

lint:
	pylint setup.py lbz examples tests
	mypy setup.py lbz # examples tests # TODO: extend for tests and if possible for examples
	flake8 setup.py lbz examples tests
