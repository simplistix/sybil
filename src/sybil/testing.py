import copy
import types
from collections.abc import Callable, Sequence
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from sybil import Sybil, Document
from sybil.typing import Parser, Lexer, LexemeMapping


def check_sybil(sybil: Sybil, text: str) -> Document:
    """
    Run the supplied text through the supplied Sybil instance and evaluate the single
    example it contains.
    """
    with NamedTemporaryFile() as temp:
        temp.write(text.encode())
        temp.flush()
        document = sybil.parse(Path(temp.name))
    examples = list(document.examples())
    assert len(examples) == 1, f'Expected exactly one example, got: {examples}'
    examples[0].evaluate()
    return document


def check_parser(parser: Parser, text: str) -> Document:
    """
    Run the supplied text through the supplied parser and evaluate the single
    example it contains.

    This is for testing :data:`~sybil.typing.Parser` implementations.
    """
    sybil = Sybil(parsers=[parser], pattern='*')
    return check_sybil(sybil, text)


def check_lexer(
    lexer: Lexer, source_text: str, expected_text: str, expected_lexemes: LexemeMapping
) -> None:
    """
    Run the supplied text through the supplied lexer make sure it lexes a single
    region and captures the expected text and lexemes.

    This is for testing :data:`~sybil.typing.Lexer` implementations.
    """
    document = Document(source_text, 'sample.txt')
    regions = list(lexer(document))
    assert len(regions) == 1, f'Expected exactly one region, got: {regions}'
    region = regions[0]
    assert expected_text == document.text[region.start : region.end]
    assert region.lexemes == expected_lexemes


def run_pytest(
    *tests: Callable[..., Any],
    fixtures: Sequence[Callable[..., Any]] = (),
    expected_failed: int = 0,
) -> None:
    """
    Run the supplied test functions in-process using pytest, with the supplied fixtures,
    and assert that the expected number of tests ran and failed.

    :param tests: The test functions to run.
    :param fixtures: A fixture function, or sequence of fixture functions, needed by the tests.
    :param expected_failed: The number of tests expected to fail, defaulting to ``0``.
    """
    # local imports in case pytest is not available
    import pytest
    from _pytest.config import get_config
    from _pytest.main import Session
    from _pytest.runner import runtestprotocol

    # Build a virtual module containing our fixture and test functions.
    module = types.ModuleType(f'_sybil_run_pytest_{id(tests)}')
    for func in list(fixtures) + list(tests):
        setattr(module, func.__name__, func)

    # Create an isolated config using only pytest's built-in default plugins.
    # get_config() never calls parse(), so load_setuptools_entrypoints("pytest11")
    # is never called — external plugins such as pytest-django are not loaded and
    # their pytest_configure hooks never fire.
    config = get_config(args=['-p', 'no:terminal'])
    config._rootpath = Path.cwd()
    config._inipath = None
    config._inicfg = {}
    # Populate config.option with all option defaults (e.g. cacheclear=False, capture='fd').
    # Normally done by parse(); we skip parse() to avoid loading setuptools entry points.
    config._parser.optparser.parse_known_args([], namespace=config.option)
    config.option.tbstyle = 'short'
    config.known_args_namespace = copy.copy(config.option)
    config._do_configure()

    class VirtualModule(pytest.Module):
        def _getobj(self) -> object:
            return module

    failures: list[str] = []
    session = Session.from_config(config)
    config.hook.pytest_sessionstart(session=session)

    virtual_module = VirtualModule.from_parent(session, path=Path(__file__))
    session._fixturemanager.parsefactories(virtual_module)

    items = [pytest.Function.from_parent(virtual_module, name=f.__name__, callobj=f) for f in tests]

    for i, item in enumerate(items):
        nextitem = items[i + 1] if i + 1 < len(items) else None
        reports = runtestprotocol(item, nextitem=nextitem)
        for report in reports:
            if report.failed and report.when in ('setup', 'call'):
                failures.append(str(report.longrepr))

    config.hook.pytest_sessionfinish(session=session, exitstatus=0)
    config._ensure_unconfigure()

    actual_failed = len(failures)
    if actual_failed != expected_failed:
        if actual_failed == 0:
            raise AssertionError(f'Expected {expected_failed} test(s) to fail, but none did')
        failure_text = '\n\n'.join(failures)
        raise AssertionError(
            f'Expected {expected_failed} test(s) to fail, but {actual_failed} did:\n\n'
            f'{failure_text}'
        )
