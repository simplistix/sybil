import types
from collections.abc import Callable, Sequence
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from sybil import Sybil, Document
from sybil.typing import Parser, Lexer, LexemeMapping

_COLLECTION_PATH = Path(__file__).with_suffix('.py')


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

    # local import in case pytest not available
    import pytest

    module = types.ModuleType(f'_sybil_run_pytest_{id(tests)}')
    for func in list(fixtures) + list(tests):
        setattr(module, func.__name__, func)

    class VirtualModule(pytest.Module):
        def _getobj(self) -> object:
            return module

        def collect(self) -> Any:
            self.session._fixturemanager.parsefactories(self)
            for func in tests:
                yield pytest.Function.from_parent(self, name=func.__name__, callobj=func)

    class Plugin:
        def __init__(self) -> None:
            self.failure_reprs: list[str] = []

        def pytest_collect_file(self, parent: pytest.Collector, file_path: Path) -> Any:
            if file_path == _COLLECTION_PATH:
                return VirtualModule.from_parent(parent, path=file_path)

        def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
            if report.failed:
                self.failure_reprs.append(str(report.longrepr))

        def pytest_sessionfinish(self, session: pytest.Session) -> None:
            self.session = session

    plugin = Plugin()
    pytest.main(
        [str(_COLLECTION_PATH), '--noconftest', '-p', 'no:cacheprovider', '-q', '--tb=short'],
        plugins=[plugin],
    )

    expected_run = len(tests)
    actual_run = plugin.session.testscollected
    actual_failed = plugin.session.testsfailed
    assert actual_run == expected_run, (
        f'Expected {expected_run} test(s) to run, but {actual_run} ran'
    )
    if actual_failed != expected_failed:
        if actual_failed == 0:
            raise AssertionError(f'Expected {expected_failed} test(s) to fail, but none did')
        failure_text = '\n\n'.join(plugin.failure_reprs)
        raise AssertionError(
            f'Expected {expected_failed} test(s) to fail, but {actual_failed} did:\n\n'
            f'{failure_text}'
        )
