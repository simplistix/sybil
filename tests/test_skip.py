import sys
from unittest import SkipTest

import pytest

from sybil.parsers.rest import PythonCodeBlockParser, DocTestParser, SkipParser
from .helpers import parse


def test_basic() -> None:
    examples, namespace = parse('skip.txt', PythonCodeBlockParser(), SkipParser(), expected=9)
    for example in examples:
        example.evaluate()
    assert namespace['run'] == [2, 5]


def test_conditional_edge_cases() -> None:
    examples, namespace = parse(
        'skip-conditional-edges.txt',
        DocTestParser(), PythonCodeBlockParser(), SkipParser(),
        expected=9
    )
    namespace['sys'] = sys
    namespace['run'] = []
    skipped = []
    for example in examples:
        try:
            example.evaluate()
        except SkipTest as e:
            skipped.append(str(e))
    assert namespace['run'] == [1, 2]
    # we should always have one and only one skip from this document.
    assert skipped == ['only true on python 2']


def test_conditional_full() -> None:
    examples, namespace = parse('skip-conditional.txt', DocTestParser(), SkipParser(), expected=9)
    namespace['result'] = result = []
    for example in examples:
        try:
            example.evaluate()
        except SkipTest as e:
            result.append('skip:'+str(e))
    assert result == [
        'start',
        'skip:(2 > 1)',
        'good 1',
        'skip:foo',
        'skip:foo',
        'good 2',
    ]


def test_bad() -> None:
    examples, namespace = parse('skip-conditional-bad.txt', SkipParser(), expected=3)

    with pytest.raises(ValueError) as excinfo:
        examples[0].evaluate()
    assert str(excinfo.value) == 'Bad skip action: lolwut'

    with pytest.raises(ValueError) as excinfo:
        examples[1].evaluate()
    assert str(excinfo.value) == 'Cannot have condition on end'

    with pytest.raises(SyntaxError):
        examples[2].evaluate()
