from io import open
from os.path import dirname, join
from traceback import TracebackException

from _pytest._code import ExceptionInfo

from sybil.document import Document
from sybil.example import Example


def sample_path(name):
    return join(dirname(__file__), 'samples', name)


def document_from_sample(name):
    path = sample_path(name)
    with open(path, encoding='ascii') as source:
        return Document(source.read(), path)


def evaluate_region(region, namespace):
    return region.evaluator(Example(
        document=Document('', '/the/path'),
        line=0,
        column=0,
        region=region,
        namespace=namespace
    ))


def check_excinfo(excinfo: ExceptionInfo, text: str, *, lineno: int, filename: str = '/the/path'):
    assert str(excinfo.value) == text, f'{str(excinfo.value)!r} == {text!r}'
    details = TracebackException.from_exception(excinfo.value, lookup_lines=False).stack[-1]
    assert details.filename == filename, f'{details.filename!r} == {filename!r}'
    assert details.lineno == lineno, f'{details.lineno} == {lineno}'
