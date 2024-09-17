import ast
import sys
from collections.abc import Sequence, Iterable
from contextlib import contextmanager
from os.path import dirname, join
from pathlib import Path
from shutil import copytree
from tempfile import NamedTemporaryFile
from textwrap import dedent
from traceback import TracebackException
from typing import Optional, Tuple, List, Union
from unittest import TextTestRunner, main as unittest_main, SkipTest

from pytest import CaptureFixture, ExceptionInfo, main as pytest_main
from seedir import seedir
from testfixtures import compare

from sybil import Sybil
from sybil.document import Document
from sybil.example import Example
from sybil.python import import_cleanup
from sybil.region import Region
from sybil.typing import Parser, Lexer

HERE = Path(__file__).parent
DOCS = HERE.parent / 'docs'
SAMPLE_PATH = HERE / 'samples'


def sample_path(name) -> str:
    return str(SAMPLE_PATH / name)


def regions_and_document(name: str, lexer: Lexer) -> Tuple[Document, List[Region]]:
    path = sample_path(name)
    document = Document(Path(path).read_text(), path)
    return document, list(lexer(document))


def lex(name: str, lexer: Lexer) -> List[Region]:
    return regions_and_document(name, lexer)[1]


def region_details(
        document: Document, regions: Iterable[Region]
) -> List[Tuple[Tuple[str, Union[Region, str]], ...]]:
    # return a list of tuple of tuples to make failures easier to work through:
    return [(
        ('start', document.line_column(region.start)),
        ('end', document.line_column(region.end)),
        ('region', region)
    ) for region in regions]


def check_lexed_regions(name: str, lexer: Lexer, *, expected: List[Region]) -> None:
    document, actual = regions_and_document(name, lexer)
    compare(
        expected=region_details(document, expected),
        actual=region_details(document, actual),
    )


def lex_text(text: str, lexer: Lexer) -> List[Region]:
    document = Document(text, 'sample.txt')
    return list(lexer(document))


def check_lexed_text_regions(text: str, lexer: Lexer, *, expected: List[Region]) -> None:
    document = Document(text, 'sample.txt')
    actual =list(lexer(document))
    compare(
        expected=region_details(document, expected),
        actual=region_details(document, actual),
    )


def parse(name: str, *parsers: Parser, expected: int) -> Tuple[List[Example], dict]:
    document = Document.parse(sample_path(name), *parsers)
    examples = list(document)
    assert len(examples) == expected, f'{len(examples)} != {expected}: {examples!r}'
    return examples, document.namespace


def check_excinfo(example: Example, excinfo: ExceptionInfo, text: str, *, lineno: int):
    compare(str(excinfo.value), expected=text)
    details = TracebackException.from_exception(excinfo.value, lookup_lines=False).stack[-1]
    document = example.document
    assert details.filename == document.path, f'{details.filename!r} != {document.path!r}'
    assert details.lineno == lineno, f'{details.lineno} != {lineno}'


def check_path(path: str, sybil: Sybil, *, expected: int, expected_skips: Sequence[str] = ()):
    document = sybil.parse(DOCS / path)
    examples = list(document)
    actual_skips = []
    for example in examples:
        try:
            example.evaluate()
        except SkipTest as e:
            actual_skips.append(str(e))
    compare(expected, actual=len(examples))
    compare(expected=expected_skips, actual=actual_skips)


def check_text(text: str, sybil: Sybil):
    with NamedTemporaryFile() as temp:
        temp.write(text.encode('ascii'))
        temp.flush()
        document = sybil.parse(Path(temp.name))
    (example,) = document
    example.evaluate()
    return document


def check_tree(expected: str, path: str):
    raw = seedir(
        DOCS / path,
        printout=False,
        first='folders',
        sort=True,
        regex=True,
        exclude_folders=r'\..+|__pycache__'
    )
    actual = '\n'+raw.split('\n', 1)[1]
    text = compare(expected=expected.strip(), actual=actual.strip(), raises=False)
    if text:  # pragma: no cover
        text += '\n\nShould be:\n'+actual
        raise AssertionError(text)


FUNCTIONAL_TEST_DIR = join(dirname(__file__), 'functional')
PYTEST = 'pytest'
UNITTEST = 'unittest'

TEST_OUTPUT_TEMPLATES = {
    PYTEST: '{file}::{sybil}line:{line},column:{column}',
    UNITTEST: '{file},{sybil}line:{line},column:{column}'
}


class Finder:

    def __init__(self, text):
        self.text = text
        self.index = 0

    def then_find(self, substring):
        assert substring in self.text[self.index:], self.text[self.index:]
        self.index = self.text.index(substring, self.index)

    def assert_present(self, text):
        assert text in self.text, f'{self.text}\n{self.text!r}'

    def assert_not_present(self, text):
        index = self.text.find(text)
        if index > -1:
            raise AssertionError('\n'+self.text[index-500:index+500])

    def assert_has_run(
            self, integration: str, file: str, *, sybil: str = '', line: int = 1, column: int = 1
    ):
        if sybil:
            sybil=f'sybil:{sybil},'
        self.assert_present(TEST_OUTPUT_TEMPLATES[integration].format(
            sybil=sybil, file=file, line=line, column=column
        ))


class Results:

    def __init__(
        self, capsys: CaptureFixture[str], total: int, errors: int = 0, failures: int = 0,
        return_code: Optional[int] = None,
    ):
        self.total = total
        self.errors = errors
        self.failures = failures
        self.return_code = return_code
        out, err = capsys.readouterr()
        assert err == '', err
        self.out = Finder(out)


def functional_sample(name: str) -> Path:
    return Path(FUNCTIONAL_TEST_DIR) / name


def clone_functional_sample(name: str, target: Path) -> Path:
    source = functional_sample(name)
    dest = target / name
    copytree(str(source), str(dest))
    return dest


def run_pytest(capsys: CaptureFixture[str], path: Path) -> Results:
    class CollectResults:
        def pytest_sessionfinish(self, session):
            self.session = session

    results = CollectResults()
    return_code = pytest_main(['-vvs', str(path), '-p', 'no:doctest'],
                              plugins=[results])
    return Results(
        capsys,
        results.session.testscollected,
        failures=results.session.testsfailed,
        return_code=return_code
    )


def run_unittest(capsys: CaptureFixture[str], path: Path) -> Results:
    runner = TextTestRunner(verbosity=2, stream=sys.stdout)
    main = unittest_main(
        exit=False, module=None, testRunner=runner,
        argv=['x', 'discover', '-v', '-t', str(path), '-s', str(path)]
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


def run(capsys: CaptureFixture[str], integration: str, path: Path) -> Results:
    return RUNNERS[integration](capsys, path)


CONFIG_TEMPLATE = """
from sybil import Sybil
from sybil.parsers.rest import PythonCodeBlockParser
from sybil.parsers.rest import DocTestParser
from sybil.parsers.rest import SkipParser
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


def write_config(tmp_path: Path, integration: str, template=CONFIG_TEMPLATE, **params: str):
    import sys
    sys.modules.pop('test_docs', None)
    params_ = {'parsers': '[DocTestParser()]'}
    params_.update(params)
    config = dedent(template).format(
        assigned_name=CONFIG_ASSIGNED_NAME[integration],
        params='\n'.join([f'    {name}={value},' for name, value in params_.items()]),
        integration=integration,
    )
    (tmp_path / CONFIG_FILENAMES[integration]).write_text(config, 'ascii')


def write_doctest(tmp_path: Path, *path: str) -> Path:
    file_path = tmp_path.joinpath(*path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(f">>> assert '{file_path.name}' == '{file_path.name}'")
    return file_path


@contextmanager
def add_to_python_path(path: Path):
    with import_cleanup():
        sys.path.append(str(path))
        yield
        sys.path.pop()


def ast_docstrings(python_source_code: str) -> Sequence[str]:
    for node in ast.walk(ast.parse(python_source_code)):
        try:
            docstring = ast.get_docstring(node, clean=False)
        except TypeError:
            pass
        else:
            if docstring:
                yield docstring
