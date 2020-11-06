import os
import sys
from fnmatch import fnmatch
from os.path import join, dirname, abspath, split

from .document import Document


class PathFilter(object):

    def __init__(self, patterns, filenames, excludes):
        self.patterns = patterns
        self.filenames = filenames
        self.excludes = excludes

    def __call__(self, path):
        path = str(path)
        return (
            (any(fnmatch(path, e) for e in self.patterns) or (split(path)[-1] in self.filenames))
            and not any(fnmatch(path, e) for e in self.excludes)
        )


def listdir(root):
    root_to_ignore = len(root) + 1
    for directory, _, filenames in os.walk(root):
        for filename in filenames:
            yield os.path.join(directory, filename)[root_to_ignore:]


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
      
    :param patterns:
      An optional sequence of :func:`patterns <fnmatch.fnmatch>` used to match documentation source
      files that will be parsed for examples.

    :param filenames:
      An optional :class:`set` of source file names that, if found anywhere within the
      root ``path`` or its sub-directories, that will be parsed for examples.

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

    :param encoding:
      An optional string specifying the encoding to be used when decoding documentation
      source files.
    """
    def __init__(self, parsers, pattern='', path='.',
                 setup=None, teardown=None, fixtures=(),
                 filenames=(), excludes=(),
                 encoding='utf-8', patterns=()):
        self.parsers = parsers
        calling_filename = sys._getframe(1).f_globals.get('__file__')
        if calling_filename:
            start_path = join(dirname(calling_filename), path)
        else:
            start_path = path
        self.path = abspath(start_path)
        patterns = list(patterns)
        if pattern:
            patterns.append(pattern)
        self.should_test_path = PathFilter(patterns, filenames, excludes)
        self.setup = setup
        self.teardown = teardown
        self.fixtures = fixtures
        self.encoding = encoding

    def parse(self, path):
        return Document.parse(path, *self.parsers, encoding=self.encoding)

    def all_documents(self):
        for path in sorted(listdir(self.path)):
            if self.should_test_path(path):
                yield self.parse(join(self.path, path))

    def pytest(self, class_=None):
        """
        The helper method for when you use :ref:`pytest_integration`.
        """
        from .integration.pytest import pytest_integration, SybilFile
        if class_ is None:
            class_ = SybilFile
        return pytest_integration(self, class_)

    def unittest(self):
        """
        The helper method for when you use :ref:`unitttest_integration`.
        """
        from .integration.unittest import unittest_integration
        return unittest_integration(self)

