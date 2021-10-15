import sys
from unittest import SkipTest

import pytest

from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.skip import skip
from .helpers import parse


def test_basic():
    examples, namespace = parse('skip.txt', PythonCodeBlockParser(), skip, expected=9)
    for example in examples:
        example.evaluate()
    assert namespace['run'] == [2, 5]


def test_conditional_edge_cases():
    examples, namespace = parse(
        'skip-conditional-edges.txt', DocTestParser(), PythonCodeBlockParser(), skip, expected=9
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


def test_conditional_full():
    examples, namespace = parse('skip-conditional.txt', DocTestParser(), skip, expected=9)
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


def test_bad():
    examples, namespace = parse('skip-conditional-bad.txt', skip, expected=3)

    with pytest.raises(ValueError) as excinfo:
        examples[0].evaluate()
    assert str(excinfo.value) == 'Bad skip action: lolwut'

    with pytest.raises(ValueError) as excinfo:
        examples[1].evaluate()
    assert str(excinfo.value) == 'Cannot have condition on end'

    with pytest.raises(SyntaxError):
        examples[2].evaluate()
