from pathlib import Path

from testfixtures import compare

from sybil.parsers.markdown.lexers import FencedCodeBlockLexer, DirectiveInHTMLCommentLexer
from sybil.parsers.myst.lexers import (
    DirectiveLexer,
    DirectiveInPercentCommentLexer
)
from sybil.region import Region
from .helpers import lex, sample_path, lex_text, check_lexed_regions, check_lexed_text_regions


def test_fenced_code_block():
    lexer = FencedCodeBlockLexer('py?thon')
    check_lexed_regions('myst-lexers.md', lexer, expected=[
        Region(36, 59, lexemes={'language': 'python', 'source': '>>> 1+1\n2\n'}),
        Region(1137, 1173, lexemes={'language': 'pthon', 'source': 'assert 1 + 1 == 2\n'}),
    ])


def test_fenced_code_block_with_mapping():
    lexer = FencedCodeBlockLexer('python', mapping={'source': 'body'})
    check_lexed_regions('myst-lexers.md', lexer, expected=[
        Region(36, 59, lexemes={'body': '>>> 1+1\n2\n'})
    ])


def test_myst_directives():
    lexer = DirectiveLexer(directive='[^}]+')
    check_lexed_regions('myst-lexers.md', lexer, expected=[
        Region(110, 148, lexemes={
            'directive': 'code-block',
            'arguments': 'python',
            'options': {},
            'source': '>>> 1 + 1\n3\n',
        }),
        Region(188, 276, lexemes={
            'directive': 'directivename',
            'arguments': 'arguments',
            'options': {'key1': 'val1', 'key2': 'val2'},
            'source': 'This is\ndirective content\n',
        }),
        Region(330, 381, lexemes={
            'directive': 'eval-rst',
            'arguments': '',
            'options': {},
            'source': '.. doctest::\n\n    >>> 1 + 1\n    4\n',
        }),
        Region(1398, 1479, lexemes={
            'directive': 'foo',
            'arguments': 'bar',
            'options': {'key1': 'val1'},
            'source': 'This, too, is a directive content\n',
        }),
    ])


def test_examples_from_parsing_tests():
    lexer = DirectiveLexer(directive='code-block', arguments='python')
    compare(lex('myst-codeblock.md', lexer), expected=[
        Region(99, 154, lexemes={
            'directive': 'code-block',
            'arguments': 'python',
            'options': {},
            'source': "raise Exception('boom!')\n",
        }),
        Region(701, 753, lexemes={
            'directive': 'code-block',
            'arguments': 'python',
            'options': {},
            'source': 'define_this = 1\n\n',
        }),
    ])


def test_myst_directives_with_mapping():
    lexer = DirectiveLexer(directive='directivename', arguments='.*', mapping={'arguments': 'foo'})
    compare(lex('myst-lexers.md', lexer), expected=[
        Region(188, 276, lexemes={'foo': 'arguments', 'options': {}}),
    ])


def test_myst_percent_comment_invisible_directive():
    lexer = DirectiveInPercentCommentLexer(
        directive='(invisible-)?code(-block)?'
    )
    compare(lex('myst-lexers.md', lexer), expected=[
        Region(449, 504, lexemes={
            'directive': 'invisible-code-block', 'arguments': 'python',
            'source': '\nb = 5\n\n...etc...\n',
        }),
        Region(584, 652, lexemes={
            'directive': 'code-block', 'arguments': 'py',
            'source': '\nb = 6\n...etc...\n\n',
        }),
    ])


def test_myst_percent_comment_invisible_directive_mapping():
    lexer = DirectiveInPercentCommentLexer(
        directive='inv[^:]+', arguments='python', mapping={'arguments': 'language'}
    )
    compare(lex('myst-lexers.md', lexer), expected=[
        Region(449, 504, lexemes={'language': 'python'}),
    ])


def test_myst_html_comment_invisible_directive():
    lexer = DirectiveInHTMLCommentLexer(
        directive='(invisible-)?code(-block)?'
    )
    compare(lex('myst-lexers.md', lexer), show_whitespace=True, expected=[
        Region(702, 827, lexemes={
            'directive': 'invisible-code-block', 'arguments': 'python',
            'source': (
                'def foo():\n'
                '   return 42\n\n'
                'meaning_of_life = 42\n\n'
                'assert foo() == meaning_of_life()\n'
            ),
        }),
        Region(912, 1015, lexemes={
            'directive': 'code-block', 'arguments': 'python',
            'source': (
                '\n'
                'blank line above ^^\n'
                '\n'
                'blank line below:\n'
                '\n'
            ),
        }),
        Region(1229, 1332, lexemes={
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


def test_myst_html_comment_invisible_skip_directive():
    lexer = DirectiveInHTMLCommentLexer(directive='skip')
    compare(lex('myst-lexers.md', lexer), show_whitespace=True, expected=[
        Region(1482, 1498, lexemes={
            'directive': 'skip',
            'arguments': 'next',
            'source': '',
        }),
        Region(1503, 1562, lexemes={
            'directive': 'skip',
            'arguments': 'start if("some stuff here", reason=\'Something\')' ,
            'source': '',
        }),
        Region(1567, 1584, lexemes={
            'directive': 'skip',
            'arguments': 'and',
            'source': '',
        }),
        Region(1589, 1647, lexemes={
            'directive': 'skip',
            'arguments': 'end',
            'source': '\n\n\nOther stuff here just gets ignored\n\n',
        }),
        Region(1652, 1672, lexemes={
            'directive': 'skip',
            'arguments': 'also',
            'source': '',
        }),
    ])


def test_myst_html_comment_invisible_clear_directive():
    lexer = DirectiveInHTMLCommentLexer('clear-namespace')
    compare(lex('myst-lexers.md', lexer), show_whitespace=True, expected=[
        Region(1678, 1699, lexemes={
            'directive': 'clear-namespace',
            'arguments': '',
            'source': '',
        }),
    ])


def test_lexing_directives():
    lexer = DirectiveLexer('[^}]+')
    compare(lex('myst-lexing-directives.md', lexer), expected=[
        Region(55, 236, lexemes={
            'directive': 'note',
            'arguments': 'This is a note admonition.',
            'options': {},
            'source': ('This is the second line of the first paragraph.\n'
                       '\n'
                       '- The note contains all indented body elements\n'
                       '  following.\n'
                       '- It includes this bullet list.\n'),
        }),
        Region(238, 320, lexemes={
            'directive': 'admonition',
            'arguments': 'And, by the way...',
            'options': {},
            'source': 'You can make up your own admonition too.\n',
        }),
        Region(322, 386, lexemes={
            'directive': 'sample',
            'arguments': '',
            'options': {},
            'source': 'This directive has no arguments, just a body.\n',
        }),
        Region(455, 481, lexemes={
            'directive': 'image',
            'arguments': 'picture.png',
            'options': {},
            'source': '',
        }),
        Region(483, 595, lexemes={
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
        Region(597, 1314, lexemes={
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
        Region(1317, 1452, lexemes={
            'directive': 'topic',
            'arguments': 'Topic Title',
            'options': {},
            'source': ('Subsequent indented lines comprise\n'
                       'the body of the topic, and are\n'
                       'interpreted as body elements.\n')
        }),
        Region(1506, 1592, lexemes={
            'directive': 'topic',
            'arguments': 'example.cfg',
            'options': {'class': 'read-file'},
            'source': '::\n\n  [A Section]\n  dir = frob\n'
        }),
        Region(1612, 1804, lexemes={
            'directive': 'sidebar',
            'arguments': 'Optional Sidebar Title',
            'options': {'subtitle': 'Optional Sidebar Subtitle'},
            'source': ('Subsequent indented lines comprise\n'
                       'the body of the sidebar, and are\n'
                       'interpreted as body elements.\n')
        }),
        Region(1807, 2006, lexemes={
            'directive': 'code-block',
            'arguments': 'python',
            'options': {'lineno-start': 10, 'emphasize-lines': '1, 3',
                        'caption': 'This is my\nmulti-line caption. It is *pretty nifty* ;-)\n'},
            'source': "a = 2\nprint('my 1st line')\nprint(f'my {a}nd line')\n",
        }),
        Region(2008, 2213, lexemes={
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


def test_directive_no_trailing_newline():
    lexer = DirectiveLexer(directive='toctree')
    text = Path(sample_path('myst-directive-no-trailing-newline.md')).read_text().rstrip('\n')
    compare(lex_text(text, lexer), expected=[
        Region(16, 67, lexemes={
            'directive': 'toctree',
            'arguments': '',
            'options': {'maxdepth': '1'},
            'source': 'flask\npyramid\ncustom\n',
        }),
    ])


def test_directive_nested():
    lexer = DirectiveLexer(directive='.+')
    text = Path(sample_path('myst-directive-nested.md')).read_text().rstrip('\n')
    check_lexed_text_regions(text, lexer, expected=[
        Region(54, 97, lexemes={
            'directive': 'warning',
            'arguments': '',
            'options': {},
            'source': "Here's my warning\n",
        }),
        Region(146, 222, lexemes={
            'directive': 'warning',
            'arguments': '',
            'options': {},
            'source': "Here's my raw text warning that isn't parsed...\n",
        }),
        Region(0, 227, lexemes={
            'directive': 'note',
            'arguments': '',
            'options': {},
            'source': ('The warning block will be properly-parsed\n'
                       '\n'
                       '   ```{warning}\n'
                       "   Here's my warning\n"
                       '   ```\n'
                       '\n'
                       'But the next block will be parsed as raw text\n'
                       '\n'
                       '    ```{warning}\n'
                       "    Here's my raw text warning that isn't parsed...\n"
                       '    ```\n'),
        }),
    ])


def test_complicated_nesting():
    lexer = DirectiveLexer(directive='.+')
    check_lexed_regions('myst-complicated-nesting.md', lexer, expected=[
        Region(37, 79, lexemes={
            'directive': 'py:module',
            'arguments': 'bytewax.connectors.demo',
            'options': {},
            'source': "",
        }),
        Region(81, 160, lexemes={
            'directive': 'autodoc2-docstring',
            'arguments': 'bytewax.connectors.demo',
            'options': {'parser': 'myst', 'allowtitles': ''},
            'source': "",
        }),
        Region(248, 315, lexemes={
            'directive': 'autodoc2-docstring',
            'arguments': 'bytewax.connectors.demo.X',
            'options': {'parser': 'myst'},
            'source': "",
        }),
        Region(171, 321, lexemes={
            'directive': 'py:data',
            'arguments': 'X',
            'options': {'canonical': 'bytewax.connectors.demo.X', 'type': 'typing.TypeVar'},
            'source': "```{autodoc2-docstring} bytewax.connectors.demo.X\n"
                      ":parser: myst\n"
                      "```\n\n",
        }),
        Region(789, 873, lexemes={
            'directive': 'autodoc2-docstring',
            'arguments': 'bytewax.connectors.demo.RandomMetricSource',
            'options': {'parser': 'myst'},
            'source': "",
        }),
        Region(875, 905, lexemes={
            'directive': 'rubric',
            'arguments': 'Initialization',
            'options': {},
            'source': "",
        }),
        Region(907, 1000, lexemes={
            'directive': 'autodoc2-docstring',
            'arguments': 'bytewax.connectors.demo.RandomMetricSource.__init__',
            'options': {'parser': 'myst'},
            'source': "",
        }),
        Region(1002, 1122, lexemes={
            'directive': 'py:method',
            'arguments': 'list_parts() -> typing.List[str]',
            'options': {'canonical': 'bytewax.connectors.demo.RandomMetricSource.list_parts'},
            'source': "",
        }),
        Region(1124, 1336, lexemes={
            'directive': 'py:method',
            'arguments': 'build_part(now: datetime.datetime, for_part: str, resume_state: '
                         'typing.Optional[bytewax.connectors.demo._RandomMetricState])',
            'options': {'canonical': 'bytewax.connectors.demo.RandomMetricSource.build_part'},
            'source': "",
        }),
        Region(336, 1343, lexemes={
            'directive': 'py:class',
            'arguments': 'RandomMetricSource(metric_name: str, interval: datetime.timedelta = '
                         'timedelta(seconds=0.7), count: int = sys.maxsize, next_random: '
                         'typing.Callable[[], float] = lambda: random.randrange(0, 10))',
            'options': {'canonical': 'bytewax.connectors.demo.RandomMetricSource'},
            'source': ":Bases:\n"
                      "    - {py:obj}`~bytewax.inputs.FixedPartitionedSource``[`{py:obj}`"
                      "~typing.Tuple``[`{py:obj}`~str``, `{py:obj}`~float``],"
                      " `{py:obj}`~bytewax.connectors.demo._RandomMetricState``]`\n\n"
                      "```{autodoc2-docstring} bytewax.connectors.demo.RandomMetricSource\n"
                      ":parser: myst\n"
                      "```\n\n"
                      "```{rubric} Initialization\n"
                      "```\n\n"
                      "```{autodoc2-docstring} "
                      "bytewax.connectors.demo.RandomMetricSource.__init__\n"
                      ":parser: myst\n"
                      "```\n\n"
                      "````{py:method} list_parts() -> typing.List[str]\n"
                      ":canonical: bytewax.connectors.demo.RandomMetricSource.list_parts\n\n"
                      "````\n\n"
                      "````{py:method} build_part(now: datetime.datetime, for_part: str, "
                      "resume_state: typing.Optional[bytewax.connectors.demo._RandomMetricState])\n"
                      ":canonical: bytewax.connectors.demo.RandomMetricSource.build_part\n\n"
                      "````\n\n",
        }),
    ])
