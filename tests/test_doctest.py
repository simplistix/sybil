from doctest import REPORT_NDIFF, ELLIPSIS

from sybil.parsers.doctest import DocTestParser, FIX_BYTE_UNICODE_REPR
from tests.helpers import document_from_sample, evaluate_region


def test_pass():
    document = document_from_sample('doctest.txt')
    regions = list(DocTestParser()(document))
    assert len(regions) == 5
    namespace = document.namespace
    assert evaluate_region(regions[0], namespace) == ''
    assert namespace['y'] == 1
    assert evaluate_region(regions[1], namespace) == ''
    assert namespace['y'] == 1
    assert evaluate_region(regions[2], namespace) == ''
    assert namespace['x'] == [1, 2, 3]
    assert evaluate_region(regions[3], namespace) == ''
    assert namespace['y'] == 2
    assert evaluate_region(regions[4], namespace) == ''
    assert namespace['y'] == 2


def test_fail():
    document = document_from_sample('doctest_fail.txt')
    regions = list(DocTestParser()(document))
    assert len(regions) == 2
    assert evaluate_region(regions[0], {}) == (
        "Expected:\n"
        "    Not my output\n"
        "Got:\n"
        "    where's my output?\n"
    )
    actual = evaluate_region(regions[1], {})
    assert actual.startswith('Exception raised:')
    assert actual.endswith('Exception: boom!\n')


def test_fail_with_options():
    document = document_from_sample('doctest_fail.txt')
    regions = list(DocTestParser(optionflags=REPORT_NDIFF|ELLIPSIS)(document))
    assert len(regions) == 2
    assert evaluate_region(regions[0], {}) == (
        "Differences (ndiff with -expected +actual):\n"
        "    - Not my output\n"
        "    + where's my output?\n"
    )


def test_literals():
    document = document_from_sample('doctest_literals.txt')
    regions = list(DocTestParser(FIX_BYTE_UNICODE_REPR)(document))
    assert len(regions) == 5
    assert evaluate_region(regions[0], {}) == ''
    assert evaluate_region(regions[1], {}) == ''
    assert evaluate_region(regions[2], {}) == ''
    assert evaluate_region(regions[3], {}) == ''
    assert evaluate_region(regions[4], {}) == ''


def test_min_indent():
    document = document_from_sample('doctest_min_indent.txt')
    regions = list(DocTestParser()(document))
    assert len(regions) == 1
    namespace = document.namespace
    assert evaluate_region(regions[0], namespace) == ''
