PYTHON = python3
CONFIG = config.txt

install:
	$(PYTHON) -m pip install -e ".[dev]" 2>/dev/null || $(PYTHON) -m pip install flake8 mypy pytest build

run:
	$(PYTHON) a_maze_ing.py $(CONFIG)

debug:
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist build

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

test:
	pytest tests/ -v

build:
	$(PYTHON) -m build
	cp dist/mazegen-*.whl . 2>/dev/null || true
	cp dist/mazegen-*.tar.gz . 2>/dev/null || true

.PHONY: install run debug clean lint lint-strict test build
