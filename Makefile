PYTHON := python3
PIP := $(PYTHON) -m pip
MAIN := a_maze_ing.py
LINT_TARGETS := a_maze_ing.py  src
CONFIG ?= config.txt

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

# need to create the requirements.txt file in the end
install:
	$(PIP) install -r requirements.txt

lint:

lint:
	$(PYTHON) -m flake8 $(LINT_TARGETS)
	$(PYTHON) -m mypy $(LINT_TARGETS) --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

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
