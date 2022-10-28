# Tests for backwards compatibility
import json

from sybil.parsers.capture import parse_captures
from sybil.parsers.codeblock import CodeBlockParser, PythonCodeBlockParser
from sybil.parsers.skip import skip
from .helpers import parse


def test_imports():
    # uncomment once all the moves are done!
    from sybil.parsers.capture import parse_captures
    from sybil.parsers.codeblock import CodeBlockParser, PythonCodeBlockParser
    from sybil.parsers.doctest import DocTestParser
    from sybil.parsers.skip import skip
    pass


def test_code_block_parser_pad():
    assert CodeBlockParser('foo').pad('x', line=2) == '\n\nx'


def test_skip_parser_function():
    examples, namespace = parse('skip.txt', PythonCodeBlockParser(), skip, expected=9)
    for example in examples:
        example.evaluate()
    assert namespace['run'] == [2, 5]


def test_capture_parser_function():
    examples, namespace = parse('capture_codeblock.txt', parse_captures, expected=1)
    examples[0].evaluate()
    assert json.loads(namespace['json']) == {"a key": "value", "b key": 42}
