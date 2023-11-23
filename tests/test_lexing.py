import re

import pytest
from testfixtures import ShouldRaise, compare
from testfixtures.comparison import compare_text, compare_dict

from sybil import Lexeme
from sybil.exceptions import LexingException
from sybil.parsers.abstract.lexers import BlockLexer
from .helpers import lex, sample_path


def test_examples_from_parsing_tests():
    lexer = BlockLexer(start_pattern=re.compile('START'), end_pattern_template='END')
    path = sample_path('lexing-fail.txt')
    with ShouldRaise(LexingException(f"Could not match 'END' in {path}:\n'\\nEDN\\n'")):
        lex('lexing-fail.txt', lexer)


class TestLexemeStripping:

    @staticmethod
    def compare_lexeme(expected: Lexeme, actual: Lexeme):

        def _compare(x, y, context):
            if str(x) != str(y):
                return compare_text(x, y, context)
            return compare_dict(x.__dict__, y.__dict__, context)

        compare(expected=expected, actual=actual, comparers={Lexeme: _compare}, strict=True)

    @pytest.mark.parametrize("actual,message", [
        (Lexeme('bar', 10, 1), "'foo' (expected) != 'bar' (actual)"),
        (Lexeme('foo', 11, 1), "'offset': 10 (expected) != 11"),
        (Lexeme('foo', 10, 2), "'line_offset': 1 (expected) != 2 (actual)"),
        (Lexeme('foo', 12, 3), "line_offset': 1 (expected) != 3 (actual)\n"
                               "'offset': 10 (expected) != 12 (actual)"),
    ])
    def test_not_equal(self, actual: Lexeme, message: str):
        with ShouldRaise(AssertionError) as s:
            self.compare_lexeme(Lexeme('foo', 10, 1), actual)
        assert message in str(s.raised)

    def test_strip_no_newlines_present(self):
        self.compare_lexeme(
            actual=Lexeme('  foo  \n', 10, 1).strip_leading_newlines(),
            expected=Lexeme('  foo  \n', 10, 1)
        )

    def test_strip_one_newline_present(self):
        self.compare_lexeme(
            actual=Lexeme('\n  foo  \n', 10, 1).strip_leading_newlines(),
            expected=Lexeme('  foo  \n', 11, 2)
        )

    def test_strip_multiple_newlines_present(self):
        self.compare_lexeme(
            actual=Lexeme('\n\n\n  foo  \n', 13, 3).strip_leading_newlines(),
            expected=Lexeme('  foo  \n', 16, 6)
        )

    def test_strip_newlines_and_spaces_present(self):
        self.compare_lexeme(
            actual=Lexeme(' \n \n  foo  \n', 10, 1).strip_leading_newlines(),
            expected=Lexeme(' \n \n  foo  \n', 10, 1)
        )
