# coding=utf-8
from doctest import REPORT_NDIFF, ELLIPSIS

import pytest
from testfixtures import compare

from sybil.example import SybilFailure
from sybil.parsers.rest import DocTestParser as ReSTDocTestParser
from sybil.parsers.myst import DocTestDirectiveParser, PythonCodeBlockParser
from tests.helpers import parse, sample_path


def test_use_existing_doctest_parser():
    path = sample_path('myst-doctest-use-rest.md')
    examples, namespace = parse('myst-doctest-use-rest.md', ReSTDocTestParser(), expected=6)
    examples[0].evaluate()
    assert namespace['x'] == 2
    examples[1].evaluate()
    assert namespace['x'] == 2
    examples[2].evaluate()
    assert namespace['x'] == 3
    with pytest.raises(SybilFailure) as excinfo:
        examples[3].evaluate()
    compare(str(excinfo.value), expected = (
        f"Example at {path}, line 28, column 1 did not evaluate as expected:\n"
        "Expected:\n"
        "    3\n"
        "Got:\n"
        "    2\n"
    ))
    examples[4].evaluate()
    examples[5].evaluate()


def test_use_python_codeblock_parser():
    examples, namespace = parse('myst-doctest.md', PythonCodeBlockParser(), expected=3)
    examples[0].evaluate()
    examples[1].evaluate()
    assert namespace['x'] == 2
    examples[2].evaluate()
    assert namespace['x'] == 3


def test_fail_with_options_using_python_codeblock_parser():
    parser = PythonCodeBlockParser(doctest_optionflags=REPORT_NDIFF|ELLIPSIS)
    examples, namespace = parse('myst-doctest-fail.md', parser, expected=1)
    with pytest.raises(SybilFailure) as excinfo:
        examples[0].evaluate()
    assert excinfo.value.result == (
        "Differences (ndiff with -expected +actual):\n"
        "    - Not my output\n"
        "    + where's my output?\n"
    )


def test_use_doctest_role_parser():
    path = sample_path('myst-doctest.md')
    examples, namespace = parse('myst-doctest.md', DocTestDirectiveParser(), expected=4)
    examples[0].evaluate()
    assert namespace['y'] == 2
    examples[1].evaluate()
    examples[2].evaluate()
    with pytest.raises(SybilFailure) as excinfo:
        examples[3].evaluate()
    compare(str(excinfo.value), expected=(
        f"Example at {path}, line 45, column 1 did not evaluate as expected:\n"
        "Expected:\n"
        "    3\n"
        "Got:\n"
        "    2\n"
    ))


def test_fail_with_options_using_doctest_role_parser():
    parser = DocTestDirectiveParser(optionflags=REPORT_NDIFF|ELLIPSIS)
    examples, namespace = parse('myst-doctest-fail.md', parser, expected=1)
    with pytest.raises(SybilFailure) as excinfo:
        examples[0].evaluate()
    assert excinfo.value.result == (
        "Differences (ndiff with -expected +actual):\n"
        "    - Also not my output\n"
        "    + where's my output?\n"
    )
