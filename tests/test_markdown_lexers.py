
from sybil.parsers.markdown.lexers import RawFencedCodeBlockLexer
from sybil.region import Region
from .helpers import check_lexed_regions


def test_fenced_code_block():
    lexer = RawFencedCodeBlockLexer()
    check_lexed_regions('markdown-fenced-code-block.md', lexer, expected = [
        Region(12, 24, lexemes={'source': '<\n >\n'}),
        Region(34, 46, lexemes={'source': '<\n >\n'}),
        Region(177, 192, lexemes={'source': 'aaa\n~~~\n'}),
        Region(266, 285, lexemes={'source': 'aaa\n```\n'}),
        Region(301, 312, lexemes={'source': 'aaa\n'}),
        Region(296, 317, lexemes={'source': '~~~\naaa\n~~~\n'}),
        Region(397, 421, lexemes={'source': 'some stuff here\n~~~\n'}),
    ])
