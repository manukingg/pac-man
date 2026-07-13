PYTHON := uv run python
UV := uv

ENTRYPOINT := pac-man.py
CONFIG ?= config.json

.PHONY: all install run debug clean lint lint-strict test format help

all: install lint

install:
	$(UV) sync

run:
	$(PYTHON) $(ENTRYPOINT) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(ENTRYPOINT) $(CONFIG)

lint:
	$(UV) run flake8 .
	$(UV) run mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(UV) run flake8 .
	$(UV) run mypy . --strict

test:
	$(UV) run pytest

format:
	$(UV) run black .
	$(UV) run isort .

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf build dist *.egg-info
	rm -f .coverage

help:
	@echo "Available commands:"
	@echo "  make install                  Install dependencies"
	@echo "  make run                      Run with config.json"
	@echo "  make run CONFIG=other.json    Run with another config"
	@echo "  make debug                    Run through pdb"
	@echo "  make lint                     Run required flake8 and mypy checks"
	@echo "  make lint-strict              Run strict mypy checks"
	@echo "  make test                     Run pytest"
	@echo "  make format                   Format code"
	@echo "  make clean                    Remove caches and build artifacts"
