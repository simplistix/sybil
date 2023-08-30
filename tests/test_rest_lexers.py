from testfixtures import compare

from sybil import Document
from sybil.parsers.rest.lexers import DirectiveLexer
from sybil.region import LexedRegion
from .helpers import lex, lex_text


def test_examples_from_parsing_tests() -> None:
    lexer = DirectiveLexer(directive='code-block', arguments='python')
    compare(lex('codeblock.txt', lexer)[:2], expected=[
        LexedRegion(23, 56, {
            'directive': 'code-block', 'arguments': 'python',
            'source': 'y += 1\n',
        }),
        LexedRegion(106, 157, {
            'directive': 'code-block', 'arguments': 'python',
            'source': "raise Exception('boom!')\n",
        }),
    ])


def test_examples_from_directive_tests() -> None:
    lexer = DirectiveLexer(directive='doctest')
    compare(lex('doctest_directive.txt', lexer), expected=[
        LexedRegion(102, 136, {
            'directive': 'doctest', 'arguments': None,
            'source': '>>> 1 + 1\n2\n',
        }),
        LexedRegion(205, 249, {
            'directive': 'doctest', 'arguments': None,
            'source': '>>> 1 + 1\nUnexpected!\n',
        }),
        LexedRegion(307, 353, {
            'directive': 'doctest', 'arguments': None,
            'source': ">>> raise Exception('boom!')",
        }),
    ])


def test_directive_nested_in_md() -> None:
    lexer = DirectiveLexer(directive='doctest')
    compare(lex('doctest_rest_nested_in_md.md', lexer), expected=[
        LexedRegion(14, 47, {
            'directive': 'doctest', 'arguments': None,
            'source': '>>> 1 + 1\n3',
        }),
    ])


def test_directive_with_single_line_body_at_end_of_string() -> None:
    text = """
        My comment
    
        .. code-block:: python
            test_my_code("Hello World")
    """
    lexer = DirectiveLexer(directive='code-block')
    start = 25
    end = 95
    compare(lex_text(text, lexer), expected=[
        LexedRegion(start, end, {
            'directive': 'code-block', 'arguments': 'python',
            'source': 'test_my_code("Hello World")',
        }),
    ])
    compare(text[start:end], show_whitespace=True, expected=(
        '        .. code-block:: python\n'
        '            test_my_code("Hello World")'
    ))


def test_directive_with_multi_line_body_at_end_of_string() -> None:
    text = """
        My comment

        .. code-block:: python
            test_my_code("Hello")
            test_my_code("World")
    """
    lexer = DirectiveLexer(directive='code-block')
    start = 21
    end = 119
    compare(lex_text(text, lexer), expected=[
        LexedRegion(start, end, {
            'directive': 'code-block', 'arguments': 'python',
            'source': 'test_my_code("Hello")\ntest_my_code("World")',
        }),
    ])
    compare(text[start:end], show_whitespace=True, expected=(
        '        .. code-block:: python\n'
        '            test_my_code("Hello")\n'
        '            test_my_code("World")'
    ))
