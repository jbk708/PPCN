# Convenience aliases — all setup is handled by setup.sh

.PHONY: setup lint format typecheck test clean

setup:
	./setup.sh

lint:
	uv run ruff check scripts/ tests/
	uv run ruff format --check scripts/ tests/

format:
	uv run ruff check --fix scripts/ tests/
	uv run ruff format scripts/ tests/

typecheck:
	uv run ty check scripts/

test:
	uv run pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .ruff_cache .pytest_cache htmlcov .coverage
