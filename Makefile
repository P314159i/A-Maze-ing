PYTHON ?= python3
PIP := $(PYTHON) -m pip
FLAKE8 ?= flake8
MYPY ?= mypy
MAIN := a_maze_ing.py
CONFIG ?= config.txt

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

install:
	$(PIP) install -r requirements.txt

lint:
	$(FLAKE8) .
	$(MYPY) . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(FLAKE8) .
	$(MYPY) . --strict

test:
	$(PYTHON) -m pytest

clean:
	rm -rf __pycache__
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf build
	rm -rf dist
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: install run debug clean lint lint-strict test
