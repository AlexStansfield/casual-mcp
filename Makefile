# Project Makefile for casual-mcp

PYTHON=python
UV=uv

.PHONY: help install dev clean lint format typecheck test coverage

help:
	@echo "Usage:"
	@echo "  make install       Install base dependencies"
	@echo "  make dev           Install dev dependencies (editable + tools)"
	@echo "  make lint          Run Ruff to lint the code"
	@echo "  make format        Run Black to autoformat the code"
	@echo "  make typecheck     Run mypy for static type checks"
	@echo "  make test          Run all tests with pytest"
	@echo "  make coverage      Run tests with coverage reporting"
	@echo "  make clean         Remove all __pycache__ and .pyc files"

install:
	$(UV) pip install -e .

dev:
	$(UV) pip install -e ".[dev]"

lint:
	ruff check src/

lint-fix:
	ruff check --fix src/

format:
	ruff format src/ 

typecheck:
	mypy src/

# test:
# 	pytest -q --tb=short

# coverage:
# 	coverage run -m pytest
# 	coverage report -m

clean:
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type f -name '*.pyc' -delete
