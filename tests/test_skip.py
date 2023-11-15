import sys
from typing import Iterable
from unittest import SkipTest

import pytest
from testfixtures import ShouldRaise

from sybil import Example, Document, Region
from sybil.parsers.rest import PythonCodeBlockParser, DocTestParser, SkipParser
from .helpers import parse


def test_basic():
    examples, namespace = parse('skip.txt', PythonCodeBlockParser(), SkipParser(), expected=9)
    for example in examples:
        example.evaluate()
    assert namespace['run'] == [2, 5]


def test_conditional_edge_cases():
    examples, namespace = parse(
        'skip-conditional-edges.txt',
        DocTestParser(), SkipParser(),
        expected=8
    )
    namespace['sys'] = sys
    namespace['run'] = []
    skipped = []
    for example in examples:
        try:
            example.evaluate()
        except SkipTest as e:
            skipped.append(str(e))
    assert namespace['run'] == [1, 2, 3, 4]
    # we should always have one and only one skip from this document.
    assert skipped == ['skip 1']


def test_conditional_full():
    examples, namespace = parse('skip-conditional.txt', DocTestParser(), SkipParser(), expected=11)
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
        'skip:good reason',
    ]


def test_bad():
    examples, namespace = parse('skip-conditional-bad.txt', SkipParser(), expected=4)

    with pytest.raises(ValueError) as excinfo:
        examples[0].evaluate()
    assert str(excinfo.value) == 'Bad skip action: lolwut'

    examples[1].evaluate()

    with pytest.raises(ValueError) as excinfo:
        examples[2].evaluate()
    assert str(excinfo.value) == "Cannot have condition on 'skip: end'"

    with pytest.raises(SyntaxError):
        examples[3].evaluate()


def test_start_follows_start():
    examples, namespace = parse('skip-start-start.txt', DocTestParser(), SkipParser(), expected=7)
    namespace['result'] = result = []
    for example in examples[:2]:
        example.evaluate()
    with ShouldRaise(ValueError("'skip: start' cannot follow 'skip: start'")):
        examples[2].evaluate()
    assert result == []


def test_next_follows_start():
    examples, namespace = parse('skip-start-next.txt', DocTestParser(), SkipParser(), expected=7)
    namespace['result'] = result = []
    for example in examples[:2]:
        example.evaluate()
    with ShouldRaise(ValueError("'skip: next' cannot follow 'skip: start'")):
        examples[2].evaluate()
    assert result == []


def test_end_no_start():
    examples, namespace = parse('skip-just-end.txt', DocTestParser(), SkipParser(), expected=3)
    namespace['result'] = result = []
    examples[0].evaluate()
    with ShouldRaise(ValueError("'skip: end' must follow 'skip: start'")):
        examples[1].evaluate()
    assert result == ['good']


def test_next_follows_next():
    examples, namespace = parse('skip-next-next.txt', DocTestParser(), SkipParser(), expected=4)
    namespace['result'] = result = []
    for example in examples:
        example.evaluate()
    assert result == [1]
