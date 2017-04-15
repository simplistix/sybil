from __future__ import absolute_import

from unittest import TestCase as BaseTestCase, TestSuite


class TestCase(BaseTestCase):

    sybil = namespace = None

    def __init__(self, example):
        BaseTestCase.__init__(self)
        self.example = example

    def runTest(self):
        self.example.evaluate()

    def id(self):
        return '{},line:{},column:{}'.format(
            self.example.document.path, self.example.line, self.example.column
        )

    __str__ = __repr__ = id

    @classmethod
    def setUpClass(cls):
        if cls.sybil.setup is not None:
            cls.sybil.setup(cls.namespace)

    @classmethod
    def tearDownClass(cls):
        if cls.sybil.teardown is not None:
            cls.sybil.teardown(cls.namespace)


def unittest_integration(sybil):

    def load_tests(loader=None, tests=None, pattern=None):
        suite = TestSuite()
        for document in sybil.all_documents():

            case = type(document.path, (TestCase, ), dict(
                sybil=sybil, namespace=document.namespace,
            ))

            for example in document:
                suite.addTest(case(example))

        return suite

    return load_tests
