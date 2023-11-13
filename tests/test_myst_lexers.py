from testfixtures import compare

from sybil.parsers.myst.lexers import (
    DirectiveLexer,
    DirectiveInPercentCommentLexer
)
from sybil.parsers.markdown.lexers import FencedCodeBlockLexer, DirectiveInHTMLCommentLexer
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
    lexer = DirectiveLexer(directive='[^}]+')
    compare(lex('myst-lexers.md', lexer), expected=[
        LexedRegion(110, 145, {
            'directive': 'code-block',
            'arguments': 'python',
            'options': {},
            'source': '>>> 1 + 1\n3\n',
        }),
        LexedRegion(188, 273, {
            'directive': 'directivename',
            'arguments': 'arguments',
            'options': {'key1': 'val1', 'key2': 'val2'},
            'source': 'This is\ndirective content\n',
        }),
        LexedRegion(330, 378, {
            'directive': 'eval-rst',
            'arguments': '',
            'options': {},
            'source': '.. doctest::\n\n    >>> 1 + 1\n    4\n',
        }),
        LexedRegion(1398, 1474, {
            'directive': 'foo',
            'arguments': 'bar',
            'options': {'key1': 'val1'},
            'source': 'This, too, is a directive content\n',
        }),
    ])


def test_examples_from_parsing_tests() -> None:
    lexer = DirectiveLexer(directive='code-block', arguments='python')
    compare(lex('myst-codeblock.md', lexer), expected=[
        LexedRegion(99, 151, {
            'directive': 'code-block',
            'arguments': 'python',
            'options': {},
            'source': "raise Exception('boom!')\n",
        }),
        LexedRegion(701, 748, {
            'directive': 'code-block',
            'arguments': 'python',
            'options': {},
            'source': 'define_this = 1\n',
        }),
    ])


def test_myst_directives_with_mapping() -> None:
    lexer = DirectiveLexer(directive='directivename', arguments='.*', mapping={'arguments': 'foo'})
    compare(lex('myst-lexers.md', lexer), expected=[
        LexedRegion(188, 273, {'foo': 'arguments', 'options': {}}),
    ])


def test_myst_percent_comment_invisible_directive() -> None:
    lexer = DirectiveInPercentCommentLexer(
        directive='(invisible-)?code(-block)?'
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
        directive='(invisible-)?code(-block)?'
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
        LexedRegion(1229, 1332, {
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


def test_myst_html_comment_invisible_skip_directive() -> None:
    lexer = DirectiveInHTMLCommentLexer(directive='skip')
    compare(lex('myst-lexers.md', lexer), show_whitespace=True, expected=[
        LexedRegion(1482, 1498, {
            'directive': 'skip',
            'arguments': 'next',
            'source': '',
        }),
        LexedRegion(1503, 1562, {
            'directive': 'skip',
            'arguments': 'start if("some stuff here", reason=\'Something\')' ,
            'source': '',
        }),
        LexedRegion(1567, 1584, {
            'directive': 'skip',
            'arguments': 'and',
            'source': '',
        }),
        LexedRegion(1589, 1647, {
            'directive': 'skip',
            'arguments': 'end',
            'source': '\n\n\nOther stuff here just gets ignored\n\n',
        }),
        LexedRegion(1652, 1672, {
            'directive': 'skip',
            'arguments': 'also',
            'source': '',
        }),
    ])


def test_myst_html_comment_invisible_clear_directive() -> None:
    lexer = DirectiveInHTMLCommentLexer('clear-namespace')
    compare(lex('myst-lexers.md', lexer), show_whitespace=True, expected=[
        LexedRegion(1678, 1699, {
            'directive': 'clear-namespace',
            'arguments': '',
            'source': '',
        }),
    ])


def test_lexing_directives():
    lexer = DirectiveLexer('[^}]+')
    compare(lex('myst-lexing-directives.md', lexer), expected=[
        LexedRegion(55, 233, {
            'directive': 'note',
            'arguments': 'This is a note admonition.',
            'options': {},
            'source': ('This is the second line of the first paragraph.\n'
                       '\n'
                       '- The note contains all indented body elements\n'
                       '  following.\n'
                       '- It includes this bullet list.\n'),
        }),
        LexedRegion(238, 317, {
            'directive': 'admonition',
            'arguments': 'And, by the way...',
            'options': {},
            'source': 'You can make up your own admonition too.\n',
        }),
        LexedRegion(322, 383, {
            'directive': 'sample',
            'arguments': '',
            'options': {},
            'source': 'This directive has no arguments, just a body.\n',
        }),
        LexedRegion(455, 478, {
            'directive': 'image',
            'arguments': 'picture.png',
            'options': {},
            'source': '',
        }),
        LexedRegion(483, 592, {
            'directive': 'image',
            'arguments': 'picture.jpeg',
            'options': {
                'height': '100px',
                'width': '200 px',
                'scale': '50 %',
                'alt': 'alternate text',
                'align': 'right',
            },
            'source': '',
        }),
        LexedRegion(597, 1311, {
            'directive': 'figure',
            'arguments': 'picture.png',
            'options': {
                'alt': 'map to buried treasure',
                'scale': '50 %',
            },
            'source': ('This is the caption of the figure (a simple paragraph).\n'
                       '\n'
                       'The legend consists of all elements after the caption.  In this\n'
                       'case, the legend consists of this paragraph and the following\n'
                       'table:\n'
                       '\n'
                       '+-----------------------+-----------------------+\n'
                       '| Symbol                | Meaning               |\n'
                       '+=======================+=======================+\n'
                       '| .. image:: tent.png   | Campground            |\n'
                       '+-----------------------+-----------------------+\n'
                       '| .. image:: waves.png  | Lake                  |\n'
                       '+-----------------------+-----------------------+\n'
                       '| .. image:: peak.png   | Mountain              |\n'
                       '+-----------------------+-----------------------+\n'
                       '\n')
        }),
        LexedRegion(1317, 1449, {
            'directive': 'topic',
            'arguments': 'Topic Title',
            'options': {},
            'source': ('Subsequent indented lines comprise\n'
                       'the body of the topic, and are\n'
                       'interpreted as body elements.\n')
        }),
        LexedRegion(1506, 1589, {
            'directive': 'topic',
            'arguments': 'example.cfg',
            'options': {'class': 'read-file'},
            'source': '::\n\n  [A Section]\n  dir = frob\n'
        }),
        LexedRegion(1612, 1801, {
            'directive': 'sidebar',
            'arguments': 'Optional Sidebar Title',
            'options': {'subtitle': 'Optional Sidebar Subtitle'},
            'source': ('Subsequent indented lines comprise\n'
                       'the body of the sidebar, and are\n'
                       'interpreted as body elements.\n')
        }),
        LexedRegion(1807, 2003, {
            'directive': 'code-block',
            'arguments': 'python',
            'options': {'lineno-start': 10, 'emphasize-lines': '1, 3',
                        'caption': 'This is my\nmulti-line caption. It is *pretty nifty* ;-)\n'},
            'source': "a = 2\nprint('my 1st line')\nprint(f'my {a}nd line')\n",
        }),
        LexedRegion(2008, 2210, {
            'directive': 'eval-rst',
            'arguments': '',
            'options': {},
            'source': (
                '.. figure:: img/fun-fish.png\n'
                '  :width: 100px\n'
                '  :name: rst-fun-fish\n'
                '\n'
                '  Party time!\n'
                '\n'
                'A reference from inside: :ref:`rst-fun-fish`\n'
                '\n'
                'A reference from outside: :ref:`syntax/directives/parsing`\n'
            )
        }),
    ])
