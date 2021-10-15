from os.path import dirname, join
from tempfile import NamedTemporaryFile
from traceback import TracebackException
from typing import Tuple, List

from _pytest._code import ExceptionInfo

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
