.PHONY: install check lint format typecheck test run skipped

install:  ## install deps and git hooks
	uv sync
	uv tool run pre-commit install --install-hooks

check: lint typecheck test  ## everything CI runs on Python

lint:
	uv run ruff check .
	uv run ruff format --check .

format:  ## fix formatting and safe lint issues
	uv run ruff format .
	uv run ruff check --fix .

typecheck:
	uv run mypy .

test:
	uv run pytest

run:  ## Acme Shield on http://127.0.0.1:8000 (API docs at /docs)
	uv run uvicorn acme_shield.app:app --reload --port 8000

skipped:  ## which ticket tests are still waiting to be started
	uv run pytest -q -rs | grep SKIPPED || true
