.DEFAULT_GOAL=


VIRTUALENV_PATH=.venv


API_DOCS_PATH=docs/source/api


venv:
	test -d $(VIRTUALENV_PATH) || virtualenv $(VIRTUALENV_PATH) -p python3


venv.clean:
	rm -rf $(VIRTUALENV_PATH)


deps.install:
	pip install -r requirements/requirements-dev.txt
	pip install -r requirements/requirements-docs.txt
	pip install -r requirements/requirements-optional.txt


link:
	pip install -e .


prepare: deps.install link


typecheck:
	mypy .


mypy.clean:
	rm -rf .mypy_cache


.PHONY: test
test: typecheck
	python -m unittest discover -s tests/ --verbose


.PHONY: docs
docs:
	mkdir -p $(API_DOCS_PATH)
	sphinx-apidoc stackholm -f -M -o $(API_DOCS_PATH)
	python docs/source/_postprocessors/_run.py
	cd docs && make html


.PHONY: docs.clean
docs.clean:
	cd docs && make clean
	rm -rf $(API_DOCS_PATH)


clean: venv.clean mypy.clean docs.clean
