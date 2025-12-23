.PHONY: help install dev test seed

help:
	@echo "Available commands:"
	@echo "  install  - Install dependencies"
	@echo "  dev      - Run development server"
	@echo "  test     - Run tests"
	@echo "  seed     - Seed database with puzzles"

install:
	uv sync

dev:
	uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test:
	uv run pytest tests/ -v

seed:
	uv run python -m scripts.seed_puzzles
