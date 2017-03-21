import sys
from glob import glob
from os.path import join, dirname, abspath

from .document import Document
from .integration.nose import nose_integration
from .integration.pytest import pytest_integration


class Sybil(object):

    def __init__(self, parsers, pattern, path='.'):
        self.parsers = parsers
        start_dir = dirname(sys._getframe(1).f_globals.get('__file__'))
        self.path = abspath(join(start_dir, path))
        self.pattern = pattern

    def parse(self, path):
        with open(path) as source:
            text = source.read()
        document = Document(text, path)
        for parser in self.parsers:
            for region in parser(document):
                document.add(region)
        return document

    def all_examples(self):
        for path in glob(join(self.path, self.pattern)):
            for example in self.parse(path):
                yield example

    def nose(self, name=None):
        return nose_integration(self, name)

    def pytest(self):
        return pytest_integration(self)
