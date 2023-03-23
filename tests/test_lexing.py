import re

from testfixtures import ShouldRaise

from sybil.parsers.abstract.lexers import BlockLexer, LexingException
from .helpers import lex, sample_path


def test_examples_from_parsing_tests():
    lexer = BlockLexer(start_pattern=re.compile('START'), end_pattern_template='END')
    path = sample_path('lexing-fail.txt')
    with ShouldRaise(LexingException(f"Could not match 'END' in {path}:\n'\\nEDN\\n'")):
        lex('lexing-fail.txt', lexer)
