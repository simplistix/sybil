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
