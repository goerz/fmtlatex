TESTPYPI = https://testpypi.python.org/pypi

install:
	pip install .

develop:
	pip install -e .[dev]

uninstall:
	pip uninstall fmtlatex

upload:
	python setup.py register
	python setup.py sdist upload

test-upload:
	python setup.py register -r $(TESTPYPI)
	python setup.py sdist upload -r $(TESTPYPI)

test-install:
	pip install -i $(TESTPYPI) fmtlatex

test: develop
	py.test -v --doctest-modules fmtlatex.py test_fmtlatex.py

clean:
	@rm -rf __pycache__
	@rm -rf *.pyc
	@rm -rf *.egg-info

.PHONY: install develop uninstall upload test-upload test-install test clean
