import sys
from importlib import import_module

import pytest
from py.path import local

from sybil.python import import_cleanup
from .helpers import Finder


def test_finder():
    # make sure the helper above works:
    finder = Finder('foo baz bar')
    with pytest.raises(AssertionError) as info:
        finder.assert_not_present('baz')
    assert str(info.value) == '\nfoo baz bar'


def test_import_cleanup(tmpdir: local):
    (tmpdir / 'some_module.py').write('import unittest\nfoo = 1')
    (tmpdir / 'other_module.py').write('import other_module\nfoo = 1')

    initial_modules = sys.modules.copy()
    initial_path = sys.path.copy()

    with import_cleanup():
        sys.path.append(tmpdir.strpath)
        some_module = import_module('some_module')
        assert some_module.foo == 1

    assert sys.modules == initial_modules
    assert sys.path == initial_path
