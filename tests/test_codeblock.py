import __future__
import sys

import pytest

from sybil.document import Document
from sybil.parsers.codeblock import CodeBlockParser
from .helpers import check_excinfo, parse


def test_basic():
    examples, namespace = parse('codeblock.txt', CodeBlockParser(), expected=7)
    namespace['y'] = namespace['z'] = 0
    assert examples[0].evaluate() is None
    assert namespace['y'] == 1
    assert namespace['z'] == 0
    with pytest.raises(Exception) as excinfo:
        examples[1].evaluate()
    check_excinfo(examples[1], excinfo, 'boom!', lineno=11)
    assert examples[2].evaluate() is None
    assert namespace['y'] == 1
    assert namespace['z'] == 1
    assert examples[3].evaluate() is None
    assert namespace['bin'] == b'x'
    assert namespace['uni'] == u'x'
    assert examples[4].evaluate() is None
    assert 'NoVars' in namespace
    assert examples[5].evaluate() is None
    assert namespace['define_this'] == 1
    assert examples[6].evaluate() is None
    assert 'YesVars' in namespace
    assert '__builtins__' not in namespace


def future_import_checks(*future_imports):
    parser = CodeBlockParser(future_imports)
    examples, namespace = parse('codeblock_future_imports.txt', parser, expected=3)
    with pytest.raises(Exception) as excinfo:
        examples[0].evaluate()
    # check the line number of the first block, which is the hardest case:
    check_excinfo(examples[0], excinfo, 'Boom 1', lineno=3)
    with pytest.raises(Exception) as excinfo:
        examples[1].evaluate()
    # check the line number of the second block:
    check_excinfo(examples[1], excinfo, 'Boom 2', lineno=9)
    examples[2].evaluate()
    # check the line number of the third block:
    assert namespace['foo'].__code__.co_firstlineno == 15
    return namespace['foo']


def test_no_future_imports():
    future_import_checks()


def test_single_future_import():
    future_import_checks('barry_as_FLUFL')


def test_multiple_future_imports():
    future_import_checks('barry_as_FLUFL', 'print_function')


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7 or higher")
def test_functional_future_imports():
    foo = future_import_checks('annotations')
    # This will keep working but not be an effective test once PEP 563 finally lands:
    assert foo.__code__.co_flags & __future__.annotations.compiler_flag


def test_windows_line_endings(tmp_path):
    p = tmp_path / "example.txt"
    p.write_bytes(
        b'This is my example:\r\n\r\n'
        b'.. code-block:: python\r\n\r\n'
        b'    from math import cos\r\n'
        b'    x = 123\r\n\r\n'
        b'That was my example.\r\n'
    )
    document = Document.parse(str(p), CodeBlockParser())
    example, = document
    example.evaluate()
    assert document.namespace['x'] == 123
