import sys
from fnmatch import fnmatch
from glob import glob
from os import listdir
from os.path import join, dirname, abspath

from .document import Document


class FilenameFilter(object):

    def __init__(self, pattern, filenames, excludes):
        self.pattern = pattern
        self.filenames = filenames
        self.excludes = excludes

    def __call__(self, filename):
        return (
            (fnmatch(filename, self.pattern) or filename in self.filenames)
            and not any(fnmatch(filename, e) for e in self.excludes)
        )


class Sybil(object):
    """
    An object to provide test runner integration for discovering examples
    in documentation and ensuring they are correct.
    
    :param parsers: 
      A sequence of callables. See :doc:`parsers`.
      
    :param path:
      The path in which documentation source files are found, relative
      to the path of the Python source file in which this class is instantiated.

      .. note::

        This is ignored when using the :ref:`pytest integration <pytest_integration>`.
      
    :param pattern:
      An optional :func:`pattern <fnmatch.fnmatch>` used to match documentation source
      files that will be parsed for examples.
      
    :param filenames:
      An optional :class:`set` of source file names that will be parsed for examples.

    :param excludes:
      An optional  sequence of :func:`patterns <fnmatch.fnmatch>` of source file names
      that will excluded when looking for examples.

    :param setup:
      An optional callable that will be called once before any examples from
      a :class:`~sybil.document.Document` are evaluated. If provided, it is
      called with the document's :attr:`~sybil.document.Document.namespace`.
      
    :param teardown:
      An optional callable that will be called after all the examples from
      a :class:`~sybil.document.Document` have been evaluated. If provided, 
      it is called with the document's 
      :attr:`~sybil.document.Document.namespace`.
      
    :param fixtures:
      An optional sequence of strings specifying the names of fixtures to 
      be requested when using the 
      :ref:`pytest integration <pytest_integration>`. The fixtures will be 
      inserted into the document's :attr:`~sybil.document.Document.namespace`.
      All scopes of fixture are supported.
    """
    def __init__(self, parsers, pattern='', path='.',
                 setup=None, teardown=None, fixtures=(),
                 filenames=(), excludes=()):
        self.parsers = parsers
        calling_filename = sys._getframe(1).f_globals.get('__file__')
        if calling_filename:
            start_path = join(dirname(calling_filename), path)
        else:
            start_path = path
        self.path = abspath(start_path)
        self.should_test_filename = FilenameFilter(pattern, filenames, excludes)
        self.setup = setup
        self.teardown = teardown
        self.fixtures = fixtures

    def parse(self, path):
        return Document.parse(path, *self.parsers)

    def all_documents(self):
        for filename in sorted(listdir(self.path)):
            if self.should_test_filename(filename):
                yield self.parse(join(self.path, filename))

    def pytest(self):
        """
        The helper method for when you use :ref:`pytest_integration`.
        """
        from .integration.pytest import pytest_integration
        return pytest_integration(self)

    def unittest(self):
        """
        The helper method for when you use either 
        :ref:`unitttest_integration` or :ref:`nose_integration`.
        """
        from .integration.unittest import unittest_integration
        return unittest_integration(self)

    nose = unittest
