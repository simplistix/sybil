import __future__
import sys

import pytest

from sybil.document import Document
from sybil.parsers.codeblock import CodeBlockParser
from .helpers import document_from_sample, evaluate_region, check_excinfo


def test_basic():
    document = document_from_sample('codeblock.txt')
    regions = list(CodeBlockParser()(document))
    assert len(regions) == 7
    namespace = document.namespace
    namespace['y'] = namespace['z'] = 0
    assert evaluate_region(regions[0], namespace) is None
    assert namespace['y'] == 1
    assert namespace['z'] == 0
    with pytest.raises(Exception) as excinfo:
        evaluate_region(regions[1], namespace)
    check_excinfo(excinfo, 'boom!', lineno=11)
    assert evaluate_region(regions[2], namespace) is None
    assert namespace['y'] == 1
    assert namespace['z'] == 1
    assert evaluate_region(regions[3], namespace) is None
    assert namespace['bin'] == b'x'
    assert namespace['uni'] == u'x'
    assert evaluate_region(regions[4], namespace) is None
    assert 'NoVars' in namespace
    assert evaluate_region(regions[5], namespace) is None
    assert namespace['define_this'] == 1
    assert evaluate_region(regions[6], namespace) is None
    assert 'YesVars' in namespace
    assert '__builtins__' not in namespace


def future_import_checks(*future_imports):
    document = document_from_sample('codeblock_future_imports.txt')
    regions = list(CodeBlockParser(future_imports)(document))
    assert len(regions) == 3
    namespace = {}
    with pytest.raises(Exception) as excinfo:
        evaluate_region(regions[0], namespace)
    # check the line number of the first block, which is the hardest case:
    check_excinfo(excinfo, 'Boom 1', lineno=3)
    with pytest.raises(Exception) as excinfo:
        evaluate_region(regions[1], namespace)
    # check the line number of the second block:
    check_excinfo(excinfo, 'Boom 2', lineno=9)
    evaluate_region(regions[2], namespace)
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
