import sys
from glob import glob
from os.path import join, dirname, abspath

from .document import Document


class Sybil(object):
    """
    An object to provide test runner integration for discovering examples
    in documentation and ensuring they are correct.
    
    :param parsers: 
      A sequence of callables. See :doc:`parsers`.
      
    :param path:
      The path in which documentation source files are found, relative
      to the path of the Python source file in which this class is instantiated.
      
    :param pattern:
      A :mod:`glob` used to match files found in the ``path``. Matching files
      will be parsed for examples.
      
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
    def __init__(self, parsers, pattern, path='.',
                 setup=None, teardown=None, fixtures=()):
        self.parsers = parsers
        calling_filename = sys._getframe(1).f_globals.get('__file__')
        if calling_filename:
            start_path = join(dirname(calling_filename), path)
        else:
            start_path = path
        self.path = abspath(start_path)
        self.pattern = pattern
        self.setup = setup
        self.teardown = teardown
        self.fixtures = fixtures

    def parse(self, path):
        with open(path) as source:
            text = source.read()
        document = Document(text, path)
        for parser in self.parsers:
            for region in parser(document):
                document.add(region)
        return document

    def all_documents(self):
        for path in sorted(glob(join(self.path, self.pattern))):
            yield self.parse(path)

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
