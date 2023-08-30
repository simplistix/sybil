from testfixtures import compare

from sybil.parsers.myst.lexers import (
    FencedCodeBlockLexer, DirectiveLexer,
    DirectiveInPercentCommentLexer, DirectiveInHTMLCommentLexer
)
from sybil.region import LexedRegion
from .helpers import lex


def test_fenced_code_block() -> None:
    lexer = FencedCodeBlockLexer('py?thon')
    compare(lex('myst-lexers.md', lexer), expected=[
        LexedRegion(36, 56, {'language': 'python', 'source': '>>> 1+1\n2\n'}),
        LexedRegion(1137, 1168, {'language': 'pthon', 'source': 'assert 1 + 1 == 2\n'}),
    ])


def test_fenced_code_block_with_mapping() -> None:
    lexer = FencedCodeBlockLexer('python', mapping={'source': 'body'})
    compare(lex('myst-lexers.md', lexer), expected=[
        LexedRegion(36, 56, {'body': '>>> 1+1\n2\n'})
    ])


def test_myst_directives() -> None:
    lexer = DirectiveLexer(directive='[^}]+', arguments='.*')
    compare(lex('myst-lexers.md', lexer), expected=[
        LexedRegion(110, 145, {
            'directive': 'code-block', 'arguments': 'python',
            'source': '>>> 1 + 1\n3\n',
        }),
        LexedRegion(188, 273, {
            'directive': 'directivename', 'arguments': 'arguments',
            'source': 'This is\ndirective content\n',
        }),
        LexedRegion(330, 378, {
            'directive': 'eval-rst', 'arguments': '',
            'source': '.. doctest::\n\n    >>> 1 + 1\n    4\n',
        }),
        LexedRegion(1413, 1489, {
            'directive': 'foo', 'arguments': 'bar',
            'source': 'This, too, is a directive content\n',
        }),
    ])


def test_examples_from_parsing_tests() -> None:
    lexer = DirectiveLexer(directive='code-block', arguments='python')
    compare(lex('myst-codeblock.md', lexer), expected=[
        LexedRegion(99, 151, {
            'directive': 'code-block', 'arguments': 'python',
            'source': "raise Exception('boom!')\n",
        }),
        LexedRegion(701, 748, {
            'directive': 'code-block', 'arguments': 'python',
            'source': 'define_this = 1\n',
        }),
    ])


def test_myst_directives_with_mapping() -> None:
    lexer = DirectiveLexer(directive='directivename', arguments='.*', mapping={'arguments': 'foo'})
    compare(lex('myst-lexers.md', lexer), expected=[
        LexedRegion(188, 273, {'foo': 'arguments'}),
    ])


def test_myst_percent_comment_invisible_directive() -> None:
    lexer = DirectiveInPercentCommentLexer(
        directive='(invisible-)?code(-block)?', arguments='py.*'
    )
    compare(lex('myst-lexers.md', lexer), expected=[
        LexedRegion(449, 504, {
            'directive': 'invisible-code-block', 'arguments': 'python',
            'source': '\nb = 5\n\n...etc...\n',
        }),
        LexedRegion(584, 652, {
            'directive': 'code-block', 'arguments': 'py',
            'source': '\nb = 6\n...etc...\n\n',
        }),
    ])


def test_myst_percent_comment_invisible_directive_mapping() -> None:
    lexer = DirectiveInPercentCommentLexer(
        directive='inv[^:]+', arguments='python', mapping={'arguments': 'language'}
    )
    compare(lex('myst-lexers.md', lexer), expected=[
        LexedRegion(449, 504, {'language': 'python'}),
    ])


def test_myst_html_comment_invisible_directive() -> None:
    lexer = DirectiveInHTMLCommentLexer(
        directive='(invisible-)?code(-block)?', arguments='py.*'
    )
    compare(lex('myst-lexers.md', lexer), show_whitespace=True, expected=[
        LexedRegion(702, 827, {
            'directive': 'invisible-code-block', 'arguments': 'python',
            'source': (
                'def foo():\n'
                '   return 42\n\n'
                'meaning_of_life = 42\n\n'
                'assert foo() == meaning_of_life()\n'
            ),
        }),
        LexedRegion(912, 1015, {
            'directive': 'code-block', 'arguments': 'python',
            'source': (
                '\n'
                'blank line above ^^\n'
                '\n'
                'blank line below:\n'
                '\n'
            ),
        }),
        LexedRegion(1244, 1347, {
            'directive': 'invisible-code', 'arguments': 'py',
            'source': (
                '\n'
                'blank line above ^^\n'
                '\n'
                'blank line below:\n'
                '\n'
            ),
        }),
    ])
