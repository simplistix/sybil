import pytest

from .helpers import Finder


def test_finder():
    # make sure the helper above works:
    finder = Finder('foo baz bar')
    with pytest.raises(AssertionError) as info:
        finder.assert_not_present('baz')
    assert str(info.value) == '\nfoo baz bar'
