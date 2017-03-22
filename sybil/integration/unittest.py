from __future__ import absolute_import

from unittest import TestCase as BaseTestCase, TestSuite


class TestCase(BaseTestCase):

    def __init__(self, example):
        BaseTestCase.__init__(self)
        self.example = example

    def runTest(self):
        self.example.evaluate()

    def id(self):
        return '{},line:{},column:{}'.format(
            self.example.path, self.example.line, self.example.column
        )

    __str__ = __repr__ = id


def unittest_integration(sybil):

    def load_tests(loader=None, tests=None, pattern=None):
        suite = TestSuite()
        for example in sybil.all_examples():
            suite.addTest(TestCase(example))
        return suite

    return load_tests
