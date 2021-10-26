# coding=utf-8
from doctest import REPORT_NDIFF, ELLIPSIS

import pytest

from sybil.document import Document
from sybil.example import SybilFailure
from sybil.parsers.doctest import DocTestParser
from tests.helpers import sample_path, parse


def test_pass():
    examples, namespace = parse('doctest.txt', DocTestParser(), expected=5)
    examples[0].evaluate()
    assert namespace['y'] == 1
    examples[1].evaluate()
    assert namespace['y'] == 1
    examples[2].evaluate()
    assert namespace['x'] == [1, 2, 3]
    examples[3].evaluate()
    assert namespace['y'] == 2
    examples[4].evaluate()
    assert namespace['y'] == 2


def test_fail():
    examples, namespace = parse('doctest_fail.txt', DocTestParser(), expected=2)
    with pytest.raises(SybilFailure) as excinfo:
        examples[0].evaluate()
    assert excinfo.value.result == (
        "Expected:\n"
        "    Not my output\n"
        "Got:\n"
        "    where's my output?\n"
    )
    with pytest.raises(SybilFailure) as excinfo:
        examples[1].evaluate()
    actual = excinfo.value.result
    assert actual.startswith('Exception raised:')
    assert actual.endswith('Exception: boom!\n')


def test_fail_with_options():
    parser = DocTestParser(optionflags=REPORT_NDIFF|ELLIPSIS)
    examples, namespace = parse('doctest_fail.txt', parser, expected=2)
    with pytest.raises(SybilFailure) as excinfo:
        examples[0].evaluate()
    assert excinfo.value.result == (
        "Differences (ndiff with -expected +actual):\n"
        "    - Not my output\n"
        "    + where's my output?\n"
    )


def test_literals():
    parser = DocTestParser()
    examples, _ = parse('doctest_literals.txt', parser, expected=5)
    for example in examples:
        example.evaluate()


def test_min_indent():
    examples, _ = parse('doctest_min_indent.txt', DocTestParser(), expected=1)
    examples[0].evaluate()


def test_tabs():
    path = sample_path('doctest_tabs.txt')
    parser = DocTestParser()
    with pytest.raises(ValueError):
        Document.parse(path, parser)


def test_irrelevant_tabs():
    examples, _ = parse('doctest_irrelevant_tabs.txt', DocTestParser(), expected=1)
    examples[0].evaluate()


def test_unicode():
    examples, _ = parse('doctest_unicode.txt', DocTestParser(), expected=1)
    examples[0].evaluate()
