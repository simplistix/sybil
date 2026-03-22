# Agent Instructions

## Principles

- **Done means green** — a change is only complete when `./happy.sh` exits 0; do not commit until it does. If `./happy.sh` was already failing before your changes, you must fix those pre-existing failures too — or stop and ask the user how to proceed.
- **Docs for everything public** — new functionality or public API changes must have accompanying docs in `docs/*.rst`
- **Type-annotate public APIs** — all public functions and classes need type annotations; mypy is the gate

## Project Overview

Sybil is a Python library for automated testing of examples in code and documentation. It parses examples from source files and evaluates them as part of your normal test run. Supports pytest and unittest. Features: doctest parsing, Python code block parsing, capture/skip parsers, MyST/Markdown support, pluggable evaluators.

## Environment

```bash
uv sync --dev --all-extras              # setup or after pulling
rm -rf .venv && uv sync --dev --all-extras  # full reset
```

## Commands

```bash
./happy.sh                                              # all checks — required before commit
uv run pytest                                           # all tests + doctests
uv run pytest tests/test_example.py                     # single file
uv run pytest --cov=src/sybil --cov-report=term-missing # with coverage
uv run mypy src/sybil tests                             # type checking
make -C docs html                                       # build docs
uv build                                                # build sdist + wheel
```

## Architecture

`src/sybil/` — all source. Key modules:

- `sybil.py` — `Sybil`, the main class that ties parsers and integrations together
- `document.py` — `Document`, represents a file being parsed and tested
- `region.py` — `Region`, `Lexeme` — parsed regions of a document
- `example.py` — `Example`, a testable example extracted from a document
- `testing.py` — testing utilities including `check_parser` and `check_lexer`
- `python.py` — Python namespace/execution utilities
- `typing.py` — type definitions
- `integration/` — test runner integrations (`pytest`, `unittest`)
- `parsers/` — parser implementations (`rest`, `markdown`, `myst`, `abstract`)
- `evaluators/` — evaluator implementations (`doctest`, `python`, `capture`, `skip`)

Config: `pyproject.toml`. Optional dep: `pytest` extra for pytest integration.

## Notes

- The `sybil.integration.pytest` module is excluded from mypy strict checking (too many pytest internals)
- Coverage tracks both `sybil` package and `tests` directory
- The project dogfoods itself — sybil is used to test its own documentation examples via `conftest.py`
- `ShouldAssert` strings in `tests/test_testing.py` may include hardcoded line numbers — this fragility is intentional; update the number, don't work around it
