from testfixtures import ShouldAssert

from sybil import Sybil
from sybil.testing import check_sybil, check_lexer


class TestCheckSybil:

    def test_no_matches(self):
        with ShouldAssert("Expected exactly one example, got: []"):
            check_sybil(Sybil([]), "")


class TestCheckLexer:

    def test_no_matches(self):
        with ShouldAssert("Expected exactly one region, got: []"):
            check_lexer(lambda _: [], "", expected_text="", expected_lexemes={})
