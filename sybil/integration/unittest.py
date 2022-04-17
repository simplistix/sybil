from typing import TYPE_CHECKING
from unittest import TestCase as BaseTestCase, TestSuite

if TYPE_CHECKING:
    from ..sybil import Sybil


class TestCase(BaseTestCase):
    """
    TestCase class to be initialized with an example or list of examples.

    :param example:
        A single example or a list of examples.
    """

    sybil = namespace = None

    def __init__(self, example):
        BaseTestCase.__init__(self)
        self.example = example

    def runTest(self):
        if isinstance(self.example, (list, tuple)):
            if self.sybil.setup is not None:
                self.sybil.setup(self.namespace)
            for example in self.example:
                example.evaluate()
        else:
            self.example.evaluate()

    def id(self):
        if isinstance(self.example, (list, tuple)):
            return self.example[0].path
        return '{},line:{},column:{}'.format(
            self.example.path, self.example.line, self.example.column
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


def unittest_integration(sybil: 'Sybil'):

    def load_tests(loader=None, tests=None, pattern=None):
        suite = TestSuite()
        for path in sorted(sybil.path.glob('**/*')):
            if path.is_file() and sybil.should_parse(path):
                document = sybil.parse(path)

                case = type(document.path, (TestCase, ), dict(
                    sybil=sybil, namespace=document.namespace,
                ))

                for example in document:
                    suite.addTest(case(example))

        return suite

    return load_tests
