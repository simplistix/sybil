import json

import pytest

from sybil import Document
from sybil.parsers.rest import CaptureParser
from tests.helpers import sample_path, parse


def test_basic():
    examples, namespace = parse('capture.txt', CaptureParser(), expected=4)
    examples[0].evaluate()
    assert namespace['expected_listing'] == (
        'root.txt\n'
        'subdir/\n'
        'subdir/file.txt\n'
        'subdir/logs/\n'
    )
    examples[1].evaluate()
    assert namespace['foo'] == 'Third level of indentation.\n'
    examples[2].evaluate()
    assert namespace['bar'] == (
        'Second level of indentation.\n\n'
        '    Third level of indentation.\n\n.. -> foo\n'
    )
    examples[3].evaluate()
    assert namespace['another'] == (
        'example\n'
    )


def test_directive_indent_beyond_block():
    path = sample_path('capture_bad_indent1.txt')
    with pytest.raises(ValueError) as excinfo:
        Document.parse(path, CaptureParser())
    assert str(excinfo.value) == (
            "couldn't find the start of the block to match '        .. -> foo' "
            f"on line 5 of {path}"
        )


def test_directive_indent_equal_to_block():
    path = sample_path('capture_bad_indent2.txt')
    with pytest.raises(ValueError) as excinfo:
        Document.parse(path, CaptureParser())
    assert str(excinfo.value) == (
            "couldn't find the start of the block to match '    .. -> foo' "
            f"on line 5 of {path}"
        )


def test_capture_codeblock():
    examples, namespace = parse('capture_codeblock.txt', CaptureParser(), expected=1)
    examples[0].evaluate()
    assert json.loads(namespace['json']) == {"a key": "value", "b key": 42}
