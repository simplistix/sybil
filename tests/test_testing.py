from testfixtures import ShouldAssert

from sybil import Sybil
from sybil.testing import check_sybil


class TestCheckSybil:

    def test_no_matches(self):
        with ShouldAssert("Expected exactly one example, got: []"):
            check_sybil(Sybil([]), "")
