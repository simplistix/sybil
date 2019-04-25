import sys
from unittest import SkipTest

import pytest

from sybil.compat import PY3
from sybil.document import Document
from sybil.parsers.codeblock import CodeBlockParser
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.skip import skip

from .helpers import sample_path, document_from_sample, evaluate_region


def test_basic():
    document = Document.parse(sample_path('skip.txt'), CodeBlockParser(), skip)
    for example in document:
        example.evaluate()
    assert document.namespace['run'] == [2, 5]


def test_conditional_simple():
    document = Document.parse(
        sample_path('skip-conditional-simple.txt'), DocTestParser(), skip
    )
    document.namespace['sys'] = sys
    document.namespace['run'] = []
    skipped = []
    for example in document:
        try:
            example.evaluate()
        except SkipTest as e:
            skipped.append(str(e))
    assert document.namespace['run'] == [1, 2]
    # we should always have one and only one skip from this document.
    if PY3:
        assert skipped == ['only true on python 2']
    else:
        assert skipped == ['only true on python 3']


def test_conditional_full():
    document = Document.parse(
        sample_path('skip-conditional.txt'), DocTestParser(), skip
    )
    document.namespace['result'] = result = []
    for example in document:
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
    document = document_from_sample('skip-conditional-bad.txt')
    regions = list(skip(document))
    namespace = document.namespace

    with pytest.raises(ValueError) as excinfo:
        evaluate_region(regions[0], namespace)
    assert str(excinfo.value) == 'Bad skip action: lolwut'

    with pytest.raises(ValueError) as excinfo:
        evaluate_region(regions[1], namespace)
    assert str(excinfo.value) == 'Cannot have condition on end'

    with pytest.raises(SyntaxError):
        evaluate_region(regions[2], namespace)
