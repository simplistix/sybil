import sys
from glob import glob
from os.path import join, dirname, abspath

from .document import Document


class Sybil(object):

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
        for path in glob(join(self.path, self.pattern)):
            yield self.parse(path)

    def pytest(self):
        from .integration.pytest import pytest_integration
        return pytest_integration(self)

    def unittest(self):
        from .integration.unittest import unittest_integration
        return unittest_integration(self)

    nose = unittest
