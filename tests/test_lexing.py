import re

from testfixtures import ShouldRaise, compare

from sybil import LexedRegion
from sybil.parsers.abstract.lexers import BlockLexer, LexingException
from .helpers import lex, sample_path


def test_examples_from_parsing_tests() -> None:
    lexer = BlockLexer(start_pattern=re.compile('START'), end_pattern_template='END')
    path = sample_path('lexing-fail.txt')
    with ShouldRaise(LexingException(f"Could not match 'END' in {path}:\n'\\nEDN\\n'")):
        lex('lexing-fail.txt', lexer)


def test_repr() -> None:
    compare(
        str(LexedRegion(36, 56, {'language': 'python', 'foo': None, 'source': 'X'*1000})),
        expected="<LexedRegion start=36 end=56 "
                 "{'language': 'python', 'foo': None, 'source': 'XXXXXXXXXX...'}>"
    )
