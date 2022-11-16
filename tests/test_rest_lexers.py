from testfixtures import compare

from sybil.parsers.rest.lexers import DirectiveLexer
from sybil.region import LexedRegion
from .helpers import lex


def test_examples_from_parsing_tests():
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


def test_examples_from_directive_tests():
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


def test_directive_nested_in_md():
    lexer = DirectiveLexer(directive='doctest')
    compare(lex('doctest_rest_nested_in_md.md', lexer), expected=[
        LexedRegion(14, 47, {
            'directive': 'doctest', 'arguments': None,
            'source': '>>> 1 + 1\n3',
        }),
    ])
