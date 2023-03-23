# coding=utf-8
from doctest import REPORT_NDIFF, ELLIPSIS, DocTestParser as BaseDocTestParser
from pathlib import Path

import pytest
from testfixtures import compare

from sybil.document import Document, PythonDocStringDocument
from sybil.example import SybilFailure
from sybil.parsers.abstract import DocTestStringParser
from sybil.parsers.rest import DocTestParser, DocTestDirectiveParser
from .helpers import sample_path, parse, FUNCTIONAL_TEST_DIR, skip_if_37_or_older


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
    path = sample_path('doctest_fail.txt')
    examples, namespace = parse('doctest_fail.txt', DocTestParser(), expected=2)
    with pytest.raises(SybilFailure) as excinfo:
        examples[0].evaluate()
    # Note on line numbers: This test shows how the example's line number is correct
    # however, doctest doesn't do the line padding trick Sybil does with codeblocks,
    # so the line number will never be correct, it's always 1.
    compare(str(excinfo.value), expected=(
        f"Example at {path}, line 1, column 1 did not evaluate as expected:\n"
        "Expected:\n"
        "    Not my output\n"
        "Got:\n"
        "    where's my output?\n"
    ))
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


def test_directive():
    path = sample_path('doctest_directive.txt')
    examples, _ = parse('doctest_directive.txt', DocTestDirectiveParser(), expected=3)
    examples[0].evaluate()
    with pytest.raises(SybilFailure) as excinfo:
        examples[1].evaluate()
    compare(str(excinfo.value), expected = (
        f"Example at {path}, line 13, column 1 did not evaluate as expected:\n"
        "Expected:\n"
        "    Unexpected!\n"
        "Got:\n"
        "    2\n"
    ))
    with pytest.raises(SybilFailure) as excinfo:
        examples[2].evaluate()
    actual = excinfo.value.result
    assert actual.startswith('Exception raised:')
    assert actual.endswith('Exception: boom!\n')


def test_directive_with_options():
    path = sample_path('doctest_directive.txt')
    parser = DocTestDirectiveParser(optionflags=REPORT_NDIFF|ELLIPSIS)
    examples, namespace = parse('doctest_directive.txt', parser, expected=3)
    with pytest.raises(SybilFailure) as excinfo:
        examples[1].evaluate()
    compare(str(excinfo.value), expected = (
        f"Example at {path}, line 13, column 1 did not evaluate as expected:\n"
        "Differences (ndiff with -expected +actual):\n"
        "    - Unexpected!\n"
        "    + 2\n"
    ))


# Number of doctests that can't be parsed in a file when looking at the whole file source:
ROOT = Path(FUNCTIONAL_TEST_DIR)
UNPARSEABLE = {
   ROOT / 'package_and_docs' / 'src' / 'parent' / 'child' / 'module_b.py': 1,
}
MINIMUM_EXPECTED_DOCTESTS = 9


@skip_if_37_or_older()
def test_sybil_example_count(all_python_files):
    parser = DocTestStringParser()

    seen_examples_from_source = 0
    seen_examples_from_docstrings = 0

    for path, source in all_python_files:
        seen_examples_from_source += len(tuple(parser(source, path)))
        for start, end, docstring in PythonDocStringDocument.extract_docstrings(source):
            seen_examples_from_docstrings += len(tuple(parser(docstring, path)))

    assert seen_examples_from_source > MINIMUM_EXPECTED_DOCTESTS, seen_examples_from_source
    assert seen_examples_from_docstrings > MINIMUM_EXPECTED_DOCTESTS, seen_examples_from_docstrings
    assert seen_examples_from_docstrings == seen_examples_from_source


def check_sybil_against_doctest(path, text):
    skip_if_37_or_older()
    problems = []
    name = str(path)
    regions = list(DocTestStringParser()(text, path))
    sybil_examples = [region.parsed for region in regions]
    doctest_examples = BaseDocTestParser().get_examples(text, name)
    problems.append(compare(
        expected=doctest_examples, actual=sybil_examples, raises=False, show_whitespace=True
    ))
    for region in regions:
        example = region.parsed
        region_source = text[region.start:region.end]
        for name in 'source', 'want':
            expected = getattr(example, name)
            if expected not in region_source:  # pragma: no cover - Only on failures!
                problems.append(f'{region}:{name}\n{expected!r} not in {region_source!r}')
    problems = [problem for problem in problems if problem]
    if problems:  # pragma: no cover - Only on failures!
        raise AssertionError('doctests not correctly extracted:\n\n'+'\n\n'.join(problems))


def test_all_docstest_examples_extracted_from_source_correctly(python_file):
    path, source = python_file
    if path in UNPARSEABLE:
        return
    check_sybil_against_doctest(path, source)


@skip_if_37_or_older()
def test_all_docstest_examples_extracted_from_docstrings_correctly(python_file):
    path, source = python_file
    for start, end, docstring in PythonDocStringDocument.extract_docstrings(source):
        check_sybil_against_doctest(path, docstring)
