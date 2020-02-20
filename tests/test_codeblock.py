import pytest
from sybil.compat import StringIO
from sybil.document import Document
from sybil.parsers.codeblock import CodeBlockParser, compile_codeblock
from tests.helpers import document_from_sample, evaluate_region


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
    assert str(excinfo.value) == 'boom!'
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


def test_future_imports():
    document = document_from_sample('codeblock_future_imports.txt')
    regions = list(CodeBlockParser(['print_function'])(document))
    assert len(regions) == 2
    buffer = StringIO()
    namespace = {'buffer': buffer}
    assert evaluate_region(regions[0], namespace) is None
    assert buffer.getvalue() == (
        'pathalogical worst case for line numbers\n'
    )
    # the future import line drops the firstlineno by 1
    code = compile_codeblock(regions[0].parsed, document.path)
    assert code.co_firstlineno == 2
    assert evaluate_region(regions[1], namespace) is None
    assert buffer.getvalue() == (
        'pathalogical worst case for line numbers\n'
        'still should work and have good line numbers\n'
    )
    # the future import line drops the firstlineno by 1
    code = compile_codeblock(regions[1].parsed, document.path)
    assert code.co_firstlineno == 8


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
