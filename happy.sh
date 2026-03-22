#!/bin/bash
set -ex

echo "=== Syncing dependencies ==="
uv sync --all-extras --all-groups

echo "=== Tests + Coverage ==="
uv run pytest --cov=src/sybil --cov-report=term-missing --cov-fail-under=100 .

echo "=== Formatting ==="
uv run ruff format .

echo "=== Type Checking ==="
uv run mypy src tests

echo "=== Docs Build ==="
uv run make -C docs clean html SPHINXOPTS=--fail-on-warning

echo "=== All checks passed! ==="
