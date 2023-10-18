from testfixtures import compare

from sybil.parsers.rest.lexers import DirectiveInCommentLexer
from sybil.parsers.rest.lexers import DirectiveLexer
from sybil.region import LexedRegion
from .helpers import lex, lex_text


def test_examples_from_parsing_tests() -> None:
    lexer = DirectiveLexer(directive='code-block', arguments='python')
    compare(lex('codeblock.txt', lexer)[:2], expected=[
        LexedRegion(23, 56, {
            'directive': 'code-block',
            'arguments': 'python',
            'options': {},
            'source': 'y += 1\n',
        }),
        LexedRegion(106, 157, {
            'directive': 'code-block',
            'arguments': 'python',
            'options': {},
            'source': "raise Exception('boom!')\n",
        }),
    ])


def test_examples_from_directive_tests() -> None:
    lexer = DirectiveLexer(directive='doctest')
    compare(lex('doctest_directive.txt', lexer), expected=[
        LexedRegion(102, 136, {
            'directive': 'doctest',
            'arguments': None,
            'options': {},
            'source': '>>> 1 + 1\n2\n',
        }),
        LexedRegion(205, 249, {
            'directive': 'doctest',
            'arguments': None,
            'options': {},
            'source': '>>> 1 + 1\nUnexpected!\n',
        }),
        LexedRegion(307, 353, {
            'directive': 'doctest',
            'arguments': None,
            'options': {},
            'source': ">>> raise Exception('boom!')",
        }),
    ])


def test_directive_nested_in_md() -> None:
    lexer = DirectiveLexer(directive='doctest')
    compare(lex('doctest_rest_nested_in_md.md', lexer), expected=[
        LexedRegion(14, 47, {
            'directive': 'doctest',
            'arguments': None,
            'options': {},
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
            'directive': 'code-block',
            'arguments': 'python',
            'options': {},
            'source': 'test_my_code("Hello World")',
        }),
    ])
    compare(text[start:end], show_whitespace=True, expected=(
        '        .. code-block:: python\n'
        '            test_my_code("Hello World")'
    ))


def test_directive_with_multi_line_body_at_end_of_string():
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
            'directive': 'code-block',
            'arguments': 'python',
            'options': {},
            'source': 'test_my_code("Hello")\ntest_my_code("World")',
        }),
    ])
    compare(text[start:end], show_whitespace=True, expected=(
        '        .. code-block:: python\n'
        '            test_my_code("Hello")\n'
        '            test_my_code("World")'
    ))


def test_skip_lexing():
    lexer = DirectiveInCommentLexer(directive='skip')
    compare(lex('skip.txt', lexer), expected=[
        LexedRegion(70, 84, {
            'directive': 'skip', 'arguments': 'next', 'options': {}, 'source': ''
        }),
        LexedRegion(269, 284, {
            'directive': 'skip', 'arguments': 'start', 'options': {}, 'source': ''
        }),
        LexedRegion(401, 414, {
            'directive': 'skip', 'arguments': 'end', 'options': {}, 'source': ''
        }),
    ])


def test_skip_lexing_bad():
    lexer = DirectiveInCommentLexer(directive='skip')
    compare(lex('skip-conditional-bad.txt', lexer), expected=[
        LexedRegion(13, 29, {
            'directive': 'skip', 'arguments': 'lolwut', 'options': {}, 'source': ''
        }),
        LexedRegion(49, 64, {
            'directive': 'skip', 'arguments': 'start', 'options': {}, 'source': ''
        }),
        LexedRegion(65, 88, {
            'directive': 'skip', 'arguments': 'end if(1 > 2)', 'options': {}, 'source': ''
        }),
        LexedRegion(104, 179, {
            'directive': 'skip',
            'arguments': 'next if(sys.version_info < (3, 0), reason="only true on python 3"',
            'options': {},
            'source': '',
        }),
    ])


def test_arguments_without_body():
    lexer = DirectiveInCommentLexer(directive='skip')
    compare(lex('skip-conditional-edges.txt', lexer), expected=[
        LexedRegion(0, 40, {
            'directive': 'skip',
            'arguments': 'next if(True, reason="skip 1")',
            'options': {},
            'source': ''
        }),
        LexedRegion(100, 142, {
            'directive': 'skip',
            'arguments': 'start if(False, reason="skip 2")',
            'options': {},
            'source': ''
        }),
        LexedRegion(205, 218, {
            'directive': 'skip',
            'arguments': 'end',
            'options': {},
            'source': ''
        }),
    ])


def test_lexing_directives():
    lexer = DirectiveLexer('[^:]+')
    compare(lex('lexing-directives.txt', lexer), expected=[
        LexedRegion(55, 245, {
            'directive': 'note',
            'arguments': 'This is a note admonition.',
            'options': {},
            'source': ('This is the second line of the first paragraph.\n'
                       '\n'
                       '- The note contains all indented body elements\n'
                       '  following.\n'
                       '- It includes this bullet list.\n'),
        }),
        LexedRegion(246, 326, {
            'directive': 'admonition',
            'arguments': 'And, by the way...',
            'options': {},
            'source': 'You can make up your own admonition too.\n',
        }),
        LexedRegion(327, 389, {
            'directive': 'sample',
            'arguments': None,
            'options': {},
            'source': 'This directive has no arguments, just a body.\n',
        }),
        LexedRegion(457, 480, {
            'directive': 'image',
            'arguments': 'picture.png',
            'options': {},
            'source': '',
        }),
        LexedRegion(481, 598, {
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
        LexedRegion(599, 1353, {
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
        LexedRegion(1354, 1486, {
            'directive': 'topic',
            'arguments': 'Topic Title',
            'options': {},
            'source': ('Subsequent indented lines comprise\n'
                       'the body of the topic, and are\n'
                       'interpreted as body elements.\n')
        }),
        LexedRegion(1539, 1616, {
            'directive': 'topic',
            'arguments': 'example.cfg',
            'options': {'class': 'read-file'},
            'source': '::\n\n  [A Section]\n  dir = frob\n'
        }),
        LexedRegion(1635, 1818, {
            'directive': 'sidebar',
            'arguments': 'Optional Sidebar Title',
            'options': {'subtitle': 'Optional Sidebar Subtitle'},
            'source': ('Subsequent indented lines comprise\n'
                       'the body of the sidebar, and are\n'
                       'interpreted as body elements.')
        }),
    ])


def test_lexing_nested_directives():
    # This test illustrates that we can lex nested directives,
    # but the blocks overlap, so would not be parseable unless only
    # the deepest nested blocks were parsed.
    lexer = DirectiveLexer('[^:]+')
    actual = lex('lexing-nested-directives.txt', lexer)
    compare(actual, expected=[
        LexedRegion(55, 236, {
            'directive': 'note',
            'arguments': 'This is a note admonition.',
            'options': {},
            'source': (
                'This is the second line of the first paragraph.\n\n'
                '   .. admonition:: And, by the way...\n\n'
                '      You can make up your own admonition too.\n'
            ),
        }),
        LexedRegion(144, 236, {
            'directive': 'admonition',
            'arguments': 'And, by the way...',
            'options': {},
            'source': 'You can make up your own admonition too.\n',
        }),
        LexedRegion(304, 783, {
            'directive': 'image',
            'arguments': 'picture.png',
            'options': {},
            'source': (
                '.. image:: picture.jpeg\n'
                '   :height: 100px\n'
                '   :width: 200 px\n'
                '   :scale: 50 %\n'
                '   :alt: alternate text\n'
                '   :align: right\n'
                '\n'
                '.. figure:: picture.png\n'
                '   :scale: 50 %\n'
                '   :alt: map to buried treasure\n'
                '\n'
                '   This is the caption of the figure (a simple paragraph).\n'
                '\n'
                '\n'
                '    .. topic:: Topic Title\n'
                '\n'
                '        Subsequent indented lines comprise\n'
                '        the body of the topic, and are\n'
                '        interpreted as body elements.'
            ),
        }),
        LexedRegion(328, 469, {
            'directive': 'image',
            'arguments': 'picture.jpeg',
            'options': {
                'align': 'right',
                'alt': 'alternate text',
                'height': '100px',
                'scale': '50 %',
                'width': '200 px',
            },
            'source': '',
        }),
        LexedRegion(470, 783, {
            'directive': 'figure',
            'arguments': 'picture.png',
            'options': {
                'scale': '50 %',
                'alt': 'map to buried treasure'
            },
            'source': (
                'This is the caption of the figure (a simple paragraph).\n'
                ' .. topic:: Topic Title\n'
                '     Subsequent indented lines comprise\n'
                '     the body of the topic, and are\n'
                '     interpreted as body elements.'
            ),
        }),
        LexedRegion(620, 783, {
            'directive': 'topic',
            'arguments': 'Topic Title',
            'options': {},
            'source': (
                'Subsequent indented lines comprise\n'
                'the body of the topic, and are\n'
                'interpreted as body elements.'
            ),
        }),
    ])


def test_lexing_directive_in_comment_without_double_colon():
    lexer = DirectiveInCommentLexer('clear-namespace')
    compare(lex('clear.txt', lexer), expected=[
        LexedRegion(48, 67, {
            'directive': 'clear-namespace', 'arguments': None, 'options': {}, 'source': ''
        }),
    ])
