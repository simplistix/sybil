import sys
from os.path import dirname, join
from tempfile import NamedTemporaryFile
from traceback import TracebackException
from typing import Tuple, List
from unittest import TextTestRunner, main as unittest_main

from _pytest._code import ExceptionInfo
from _pytest.capture import CaptureFixture
from _pytest.config import main as pytest_main

from sybil import Sybil
from sybil.document import Document
from sybil.example import Example
from sybil.typing import Parser


def sample_path(name):
    return join(dirname(__file__), 'samples', name)


def parse(name: str, *parsers: Parser, expected: int) -> Tuple[List[Example], dict]:
    document = Document.parse(sample_path(name), *parsers)
    examples = list(document)
    assert len(examples) == expected, f'{len(examples)} != {expected}'
    return examples, document.namespace


def check_excinfo(example: Example, excinfo: ExceptionInfo, text: str, *, lineno: int):
    assert str(excinfo.value) == text, f'{str(excinfo.value)!r} != {text!r}'
    details = TracebackException.from_exception(excinfo.value, lookup_lines=False).stack[-1]
    document = example.document
    assert details.filename == document.path, f'{details.filename!r} != {document.path!r}'
    assert details.lineno == lineno, f'{details.lineno} != {lineno}'


def check_text(text: str, sybil: Sybil):
    with NamedTemporaryFile() as temp:
        temp.write(text.encode('ascii'))
        temp.flush()
        document = sybil.parse(temp.name)
    (example,) = document
    example.evaluate()
    return document


functional_test_dir = join(dirname(__file__), 'functional')


class Finder:

    def __init__(self, text):
        self.text = text
        self.index = 0

    def then_find(self, substring):
        assert substring in self.text[self.index:], self.text[self.index:]
        self.index = self.text.index(substring, self.index)

    def assert_not_present(self, text):
        index = self.text.find(text)
        if index > -1:
            raise AssertionError('\n'+self.text[index-500:index+500])


class Results:

    def  __init__(
        self, capsys: CaptureFixture[str], total: int, errors: int = 0, failures: int = 0,
        return_code: int = None,
    ):
        self.total = total
        self.errors = errors
        self.failures = failures
        self.return_code = return_code
        out, err = capsys.readouterr()
        assert err == ''
        self.out = Finder(out)


def run_pytest(capsys: CaptureFixture[str], root: str) -> Results:
    class CollectResults:
        def pytest_sessionfinish(self, session):
            self.session = session

    results = CollectResults()
    return_code = pytest_main(['-vvs', join(functional_test_dir, root)],
                              plugins=[results])
    return Results(
        capsys,
        results.session.testscollected,
        failures=results.session.testsfailed,
        return_code=return_code
    )


def run_unittest(capsys: CaptureFixture[str], root: str) -> Results:
    runner = TextTestRunner(verbosity=2, stream=sys.stdout)
    path = join(functional_test_dir, root)
    main = unittest_main(
        exit=False, module=None, testRunner=runner,
        argv=['x', 'discover', '-v', '-t', path, '-s', path]
    )
    return Results(
        capsys,
        main.result.testsRun,
        errors=len(main.result.errors),
        failures=len(main.result.failures),
    )
