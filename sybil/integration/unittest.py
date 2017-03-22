from __future__ import absolute_import

from unittest import TestCase as BaseTestCase, TestSuite


class TestCase(BaseTestCase):

    def __init__(self, example, namespace):
        BaseTestCase.__init__(self)
        self.example = example
        self.namespace = namespace

    def runTest(self):
        self.example.evaluate(self.namespace)

    def id(self):
        return '{},line:{},column:{}'.format(
            self.example.path, self.example.line, self.example.column
        )

    __str__ = __repr__ = id


def unittest_integration(sybil):

    def load_tests(loader, tests, pattern):
        namespace = {}
        suite = TestSuite()
        for example in sybil.all_examples():
            suite.addTest(TestCase(example, namespace))
        return suite

    return load_tests
