import sys
from os.path import dirname, join
from pathlib import Path
from shutil import copytree
from tempfile import NamedTemporaryFile
from traceback import TracebackException
from typing import Tuple, List
from unittest import TextTestRunner, main as unittest_main

from _pytest._code import ExceptionInfo
from _pytest.capture import CaptureFixture
from _pytest.config import main as pytest_main
from py.path import local

from sybil import Sybil
from sybil.document import Document
from sybil.example import Example
from sybil.typing import Parser


def sample_path(name) -> str:
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
        document = sybil.parse(Path(temp.name))
    (example,) = document
    example.evaluate()
    return document


FUNCTIONAL_TEST_DIR = join(dirname(__file__), 'functional')
PYTEST = 'pytest'
UNITTEST = 'unittest'

TEST_OUTPUT_TEMPLATES = {
    PYTEST: '{file}::line:{line},column:{column}',
    UNITTEST: '{file},line:{line},column:{column}'
}


class Finder:

    def __init__(self, text):
        self.text = text
        self.index = 0

    def then_find(self, substring):
        assert substring in self.text[self.index:], self.text[self.index:]
        self.index = self.text.index(substring, self.index)

    def assert_present(self, text):
        assert text in self.text, repr(self.text)

    def assert_not_present(self, text):
        index = self.text.find(text)
        if index > -1:
            raise AssertionError('\n'+self.text[index-500:index+500])

    def assert_has_run(self, integration: str, file: str, *, line: int = 1, column: int = 1):
        self.assert_present(TEST_OUTPUT_TEMPLATES[integration].format(
            file=file, line=line, column=column
        ))


class Results:

    def __init__(
        self, capsys: CaptureFixture[str], total: int, errors: int = 0, failures: int = 0,
        return_code: int = None,
    ):
        self.total = total
        self.errors = errors
        self.failures = failures
        self.return_code = return_code
        out, err = capsys.readouterr()
        assert err == '', err
        self.out = Finder(out)


def functional_sample(name: str) -> local:
    return local(FUNCTIONAL_TEST_DIR) / name


def clone_functional_sample(name: str, target: local) -> local:
    source = functional_sample(name)
    dest = target / name
    copytree(source.strpath, dest.strpath)
    return dest


def run_pytest(capsys: CaptureFixture[str], path: local) -> Results:
    class CollectResults:
        def pytest_sessionfinish(self, session):
            self.session = session

    results = CollectResults()
    return_code = pytest_main(['-vvs', path.strpath, '-p', 'no:doctest'],
                              plugins=[results])
    return Results(
        capsys,
        results.session.testscollected,
        failures=results.session.testsfailed,
        return_code=return_code
    )


def run_unittest(capsys: CaptureFixture[str], path: local) -> Results:
    runner = TextTestRunner(verbosity=2, stream=sys.stdout)
    main = unittest_main(
        exit=False, module=None, testRunner=runner,
        argv=['x', 'discover', '-v', '-t', path.strpath, '-s', path.strpath]
    )
    return Results(
        capsys,
        main.result.testsRun,
        errors=len(main.result.errors),
        failures=len(main.result.failures),
    )


RUNNERS = {
    PYTEST: run_pytest,
    UNITTEST: run_unittest,
}


def run(capsys: CaptureFixture[str], integration: str, path: local) -> Results:
    return RUNNERS[integration](capsys, path)


CONFIG_TEMPLATE = """
from sybil import Sybil
from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.skip import skip
{assigned_name} = Sybil(
{params}
).{integration}()
"""

CONFIG_FILENAMES = {
    PYTEST: 'conftest.py',
    UNITTEST: 'test_docs.py'
}

CONFIG_ASSIGNED_NAME = {
    PYTEST: 'pytest_collect_file',
    UNITTEST: 'load_tests'
}


def write_config(tmpdir: local, integration: str, **params: str) -> None:
    import sys
    sys.modules.pop('test_docs', None)
    params_ = {'parsers': '[DocTestParser()]'}
    params_.update(params)
    config = CONFIG_TEMPLATE.format(
        assigned_name = CONFIG_ASSIGNED_NAME[integration],
        params='\n'.join([f'    {name}={value},' for name, value in params_.items()]),
        integration=integration,
    )
    (tmpdir / CONFIG_FILENAMES[integration]).write_text(config, 'ascii')


def write_doctest(tmpdir: local, *path: str) -> Path:
    file_path = Path(tmpdir.join(*path).strpath)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(f">>> assert '{file_path.name}' == '{file_path.name}'")
    return file_path
