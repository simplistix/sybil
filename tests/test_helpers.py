import sys
from importlib import import_module
from pathlib import Path

import pytest

from sybil.python import import_cleanup
from .helpers import Finder, ast_docstrings


def test_finder_present_but_is_not_present():
    finder = Finder('foo\nbaz\n')
    with pytest.raises(AssertionError) as info:
        finder.assert_present('bob')
    assert str(info.value) == "foo\nbaz\n\n'foo\\nbaz\\n'"


def test_finder_not_present_but_is_present():
    finder = Finder('foo baz bar')
    with pytest.raises(AssertionError) as info:
        finder.assert_not_present('baz')
    assert str(info.value) == '\nfoo baz bar'


def test_import_cleanup(tmp_path: Path):
    (tmp_path / 'some_module.py').write_text('import unittest\nfoo = 1')
    (tmp_path / 'other_module.py').write_text('import other_module\nfoo = 1')

    initial_modules = sys.modules.copy()
    initial_path = sys.path.copy()

    with import_cleanup():
        sys.path.append(str(tmp_path))
        some_module = import_module('some_module')
        assert some_module.foo == 1

    assert sys.modules == initial_modules
    assert sys.path == initial_path


def test_all_python_files(all_python_files):
    count = len(all_python_files)
    assert count > 50, count


def test_ast_docstrings(all_python_files):
    seen_docstrings = 0
    for _, source in all_python_files:
        seen_docstrings += len(tuple(ast_docstrings(source)))
    assert seen_docstrings > 50, seen_docstrings
