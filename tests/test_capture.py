import pytest
from sybil.parsers.capture import parse_captures
from sybil.compat import PY3
from tests.helpers import document_from_sample, sample_path, evaluate_region


def test_basic():
    document = document_from_sample('capture.txt')
    regions = list(parse_captures(document))
    namespace = document.namespace
    assert evaluate_region(regions[-1], namespace) is None
    assert namespace['expected_listing'] == (
        'root.txt\n'
        'subdir/\n'
        'subdir/file.txt\n'
        'subdir/logs/\n'
    )
    assert evaluate_region(regions[-2], namespace) is None
    assert namespace['foo'] == 'Third level of indentation.\n'
    assert evaluate_region(regions[-3], namespace) is None
    assert namespace['bar'] == (
        'Second level of indentation.\n\n'
        '    Third level of indentation.\n\n.. -> foo\n'
    )
    assert evaluate_region(regions[-4], namespace) is None
    assert namespace['another'] == (
        'example\n'
    )
    assert len(regions) == 4


def test_directive_indent_beyond_block():
    document = document_from_sample('capture_bad_indent1.txt')
    with pytest.raises(ValueError) as excinfo:
        list(parse_captures(document))
    if PY3:
        block = "'        .. -> foo'"
    else:
        block = "u'        .. -> foo'"
    assert str(excinfo.value) == (
            "couldn't find the start of the block to match "+block+" "
            "on line 5 of "+sample_path('capture_bad_indent1.txt')
        )


def test_directive_indent_equal_to_block():
    document = document_from_sample('capture_bad_indent2.txt')
    with pytest.raises(ValueError) as excinfo:
        list(parse_captures(document))
    if PY3:
        block = "'    .. -> foo'"
    else:
        block = "u'    .. -> foo'"
    assert str(excinfo.value) == (
            "couldn't find the start of the block to match "+block+" "
            "on line 5 of "+sample_path('capture_bad_indent2.txt')
        )
