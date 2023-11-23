from testfixtures import compare

from sybil.parsers.rest.lexers import DirectiveInCommentLexer
from sybil.parsers.rest.lexers import DirectiveLexer
from sybil.region import Region
from .helpers import lex, lex_text


def test_examples_from_parsing_tests():
    lexer = DirectiveLexer(directive='code-block', arguments='python')
    compare(lex('codeblock.txt', lexer)[:2], expected=[
        Region(23, 56, lexemes={
            'directive': 'code-block',
            'arguments': 'python',
            'options': {},
            'source': 'y += 1\n',
        }),
        Region(106, 157, lexemes={
            'directive': 'code-block',
            'arguments': 'python',
            'options': {},
            'source': "raise Exception('boom!')\n",
        }),
    ])


def test_examples_from_directive_tests():
    lexer = DirectiveLexer(directive='doctest')
    compare(lex('doctest_directive.txt', lexer), expected=[
        Region(102, 136, lexemes={
            'directive': 'doctest',
            'arguments': None,
            'options': {},
            'source': '>>> 1 + 1\n2\n',
        }),
        Region(205, 249, lexemes={
            'directive': 'doctest',
            'arguments': None,
            'options': {},
            'source': '>>> 1 + 1\nUnexpected!\n',
        }),
        Region(307, 353, lexemes={
            'directive': 'doctest',
            'arguments': None,
            'options': {},
            'source': ">>> raise Exception('boom!')",
        }),
    ])


def test_directive_nested_in_md():
    lexer = DirectiveLexer(directive='doctest')
    compare(lex('doctest_rest_nested_in_md.md', lexer), expected=[
        Region(14, 47, lexemes={
            'directive': 'doctest',
            'arguments': None,
            'options': {},
            'source': '>>> 1 + 1\n3',
        }),
    ])


def test_directive_with_single_line_body_at_end_of_string():
    text = """
        My comment
    
        .. code-block:: python
            test_my_code("Hello World")
    """
    lexer = DirectiveLexer(directive='code-block')
    start = 25
    end = 95
    compare(lex_text(text, lexer), expected=[
        Region(start, end, lexemes={
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
        Region(start, end, lexemes={
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
        Region(70, 84, lexemes={
            'directive': 'skip', 'arguments': 'next', 'options': {}, 'source': ''
        }),
        Region(197, 212, lexemes={
            'directive': 'skip', 'arguments': 'start', 'options': {}, 'source': ''
        }),
        Region(329, 342, lexemes={
            'directive': 'skip', 'arguments': 'end', 'options': {}, 'source': ''
        }),
    ])


def test_skip_lexing_bad():
    lexer = DirectiveInCommentLexer(directive='skip')
    compare(lex('skip-conditional-bad.txt', lexer), expected=[
        Region(13, 29, lexemes={
            'directive': 'skip', 'arguments': 'lolwut', 'options': {}, 'source': ''
        }),
        Region(49, 64, lexemes={
            'directive': 'skip', 'arguments': 'start', 'options': {}, 'source': ''
        }),
        Region(65, 88, lexemes={
            'directive': 'skip', 'arguments': 'end if(1 > 2)', 'options': {}, 'source': ''
        }),
        Region(104, 179, lexemes={
            'directive': 'skip',
            'arguments': 'next if(sys.version_info < (3, 0), reason="only true on python 3"',
            'options': {},
            'source': '',
        }),
    ])


def test_arguments_without_body():
    lexer = DirectiveInCommentLexer(directive='skip')
    compare(lex('skip-conditional-edges.txt', lexer), expected=[
        Region(0, 40, lexemes={
            'directive': 'skip',
            'arguments': 'next if(True, reason="skip 1")',
            'options': {},
            'source': ''
        }),
        Region(100, 142, lexemes={
            'directive': 'skip',
            'arguments': 'start if(False, reason="skip 2")',
            'options': {},
            'source': ''
        }),
        Region(205, 218, lexemes={
            'directive': 'skip',
            'arguments': 'end',
            'options': {},
            'source': ''
        }),
    ])


def test_lexing_directives():
    lexer = DirectiveLexer('[^:]+')
    compare(lex('lexing-directives.txt', lexer), expected=[
        Region(55, 245, lexemes={
            'directive': 'note',
            'arguments': 'This is a note admonition.',
            'options': {},
            'source': ('This is the second line of the first paragraph.\n'
                       '\n'
                       '- The note contains all indented body elements\n'
                       '  following.\n'
                       '- It includes this bullet list.\n'),
        }),
        Region(246, 326, lexemes={
            'directive': 'admonition',
            'arguments': 'And, by the way...',
            'options': {},
            'source': 'You can make up your own admonition too.\n',
        }),
        Region(327, 389, lexemes={
            'directive': 'sample',
            'arguments': None,
            'options': {},
            'source': 'This directive has no arguments, just a body.\n',
        }),
        Region(457, 480, lexemes={
            'directive': 'image',
            'arguments': 'picture.png',
            'options': {},
            'source': '',
        }),
        Region(481, 598, lexemes={
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
        Region(599, 1353, lexemes={
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
        Region(1354, 1486, lexemes={
            'directive': 'topic',
            'arguments': 'Topic Title',
            'options': {},
            'source': ('Subsequent indented lines comprise\n'
                       'the body of the topic, and are\n'
                       'interpreted as body elements.\n')
        }),
        Region(1539, 1616, lexemes={
            'directive': 'topic',
            'arguments': 'example.cfg',
            'options': {'class': 'read-file'},
            'source': '::\n\n  [A Section]\n  dir = frob\n'
        }),
        Region(1635, 1819, lexemes={
            'directive': 'sidebar',
            'arguments': 'Optional Sidebar Title',
            'options': {'subtitle': 'Optional Sidebar Subtitle'},
            'source': ('Subsequent indented lines comprise\n'
                       'the body of the sidebar, and are\n'
                       'interpreted as body elements.\n')
        }),
        Region(1856, 1871, lexemes={
            'directive': 'skip',
            'arguments': 'next',
            'options': {},
            'source': '',
        }),
        Region(1871, 1911, lexemes={
            'directive': 'code-block',
            'arguments': 'python',
            'options': {},
            'source': (
                'run.append(1)\n'
            ),
        }),
        Region(1988, 2066, lexemes={
            'directive': 'topic',
            'arguments': 'example.cfg',
            'options': {'class': 'read-file'},
            'source': (
                '::\n\n  [A Section]\n  dir = frob\n\n'
            ),
        }),
    ])


def test_lexing_nested_directives():
    # This test illustrates that we can lex nested directives,
    # but the blocks overlap, so would not be parseable unless only
    # the deepest nested blocks were parsed.
    lexer = DirectiveLexer('[^:]+')
    actual = lex('lexing-nested-directives.txt', lexer)
    compare(actual, expected=[
        Region(55, 236, lexemes={
            'directive': 'note',
            'arguments': 'This is a note admonition.',
            'options': {},
            'source': (
                'This is the second line of the first paragraph.\n\n'
                '   .. admonition:: And, by the way...\n\n'
                '      You can make up your own admonition too.\n'
            ),
        }),
        Region(144, 236, lexemes={
            'directive': 'admonition',
            'arguments': 'And, by the way...',
            'options': {},
            'source': 'You can make up your own admonition too.\n',
        }),
        Region(304, 783, lexemes={
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
        Region(328, 469, lexemes={
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
        Region(470, 783, lexemes={
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
        Region(620, 783, lexemes={
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
        Region(48, 67, lexemes={
            'directive': 'clear-namespace', 'arguments': None, 'options': {}, 'source': ''
        }),
    ])
