import sys
from glob import glob
from os.path import join, dirname, abspath

from .document import Document
from .integration.pytest import pytest_integration
from .integration.unittest import unittest_integration


class Sybil(object):

    def __init__(self, parsers, pattern, path='.',
                 setup=None, teardown=None, fixtures=()):
        self.parsers = parsers
        start_dir = dirname(sys._getframe(1).f_globals.get('__file__'))
        self.path = abspath(join(start_dir, path))
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
        for path in glob(join(self.path, self.pattern)):
            yield self.parse(path)

    def pytest(self):
        return pytest_integration(self)

    def unittest(self):
        return unittest_integration(self)

    nose = unittest
