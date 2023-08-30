"""
This is a module doc string.
"""  # This is a comment on how annoying 3.7 and earlier are!
from functools import partial
from pathlib import Path

from testfixtures import compare

from sybil.document import PythonDocStringDocument
from .helpers import ast_docstrings, skip_if_37_or_older


@skip_if_37_or_older()
def test_extract_docstring() -> None:
    """
    This is a function docstring.
    """
    python_source_code = Path(__file__).read_text()
    expected = list(ast_docstrings(python_source_code))
    actual = list(PythonDocStringDocument.extract_docstrings(python_source_code))
    compare(expected, actual=[text for _, _, text in actual], show_whitespace=True)
    compare(expected, actual=[python_source_code[s:e] for s, e, _ in actual], show_whitespace=True)


@skip_if_37_or_older()
def test_all_docstrings_extracted_correctly(python_file) -> None:
    problems = []
    path, source = python_file
    expected = list(ast_docstrings(source))
    actual = list(PythonDocStringDocument.extract_docstrings(source))
    check = partial(compare, prefix=str(path), raises=False, show_whitespace=True)
    for check_result in (
        check(expected=len(expected), actual=len(actual)),
        check(expected, actual=[text for _, _, text in actual]),
        check(expected, actual=[source[s:e] for s, e, _ in actual]),
    ):
        if check_result:  # pragma: no cover - Only on failures!
            problems.append(check_result)
    if problems:  # pragma: no cover - Only on failures!
        raise AssertionError('docstrings not correctly extracted:\n\n'+'\n\n'.join(problems))
