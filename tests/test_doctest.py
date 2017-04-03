from doctest import REPORT_NDIFF, ELLIPSIS

from sybil import DocTestParser
from sybil.parsers.doctest import FIX_BYTE_UNICODE_REPR
from tests.helpers import document_from_sample


def test_pass():
    document = document_from_sample('doctest.txt')
    regions = list(DocTestParser()(document))
    assert len(regions) == 5
    namespace = document.namespace
    assert regions[0].evaluate(namespace) == ''
    assert namespace['y'] == 1
    assert regions[1].evaluate(namespace) == ''
    assert namespace['y'] == 1
    assert regions[2].evaluate(namespace) == ''
    assert namespace['x'] == [1, 2, 3]
    assert regions[3].evaluate(namespace) == ''
    assert namespace['y'] == 2
    assert regions[4].evaluate(namespace) == ''
    assert namespace['y'] == 2


def test_fail():
    document = document_from_sample('doctest_fail.txt')
    regions = list(DocTestParser()(document))
    assert len(regions) == 2
    assert regions[0].evaluate({}) == (
        "Expected:\n"
        "    Not my output\n"
        "Got:\n"
        "    where's my output?\n"
    )
    actual = regions[1].evaluate({})
    assert actual.startswith('Exception raised:')
    assert actual.endswith('Exception: boom!\n')


def test_fail_with_options():
    document = document_from_sample('doctest_fail.txt')
    regions = list(DocTestParser(optionflags=REPORT_NDIFF|ELLIPSIS)(document))
    assert len(regions) == 2
    assert regions[0].evaluate({}) == (
        "Differences (ndiff with -expected +actual):\n"
        "    - Not my output\n"
        "    + where's my output?\n"
    )


def test_literals():
    document = document_from_sample('doctest_literals.txt')
    regions = list(DocTestParser(FIX_BYTE_UNICODE_REPR)(document))
    assert len(regions) == 4
    assert regions[0].evaluate({}) == ''
    assert regions[1].evaluate({}) == ''
    assert regions[2].evaluate({}) == ''
    assert regions[3].evaluate({}) == ''
