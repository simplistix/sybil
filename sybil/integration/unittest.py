from collections.abc import Callable
from typing import Any, Dict, Optional
from unittest import TestCase as BaseTestCase, TestSuite
from unittest.loader import TestLoader

from sybil import Sybil
from sybil.example import Example


class TestCase(BaseTestCase):

    sybil: Sybil
    namespace: Dict[str, Any]

    def __init__(self, example: Example) -> None:
        BaseTestCase.__init__(self)
        self.example = example

    def runTest(self) -> None:
        self.example.evaluate()

    def id(self) -> str:
        return f'{self.example.path},{self.sybil.identify(self.example)}'

    __str__ = __repr__ = id

    @classmethod
    def setUpClass(cls) -> None:
        if cls.sybil.setup is not None:
            cls.sybil.setup(cls.namespace)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.sybil.teardown is not None:
            cls.sybil.teardown(cls.namespace)


def unittest_integration(
    *sybils: Sybil,
) -> Callable[[Optional[TestLoader], Optional[TestSuite], Optional[str]], TestSuite]:

    def load_tests(
        loader: Optional[TestLoader] = None,
        tests: Optional[TestSuite] = None,
        pattern: Optional[str] = None,
    ) -> TestSuite:
        suite = TestSuite()
        for sybil in sybils:
            for path in sorted(sybil.path.glob('**/*')):
                if path.is_file() and sybil.should_parse(path):
                    document = sybil.parse(path)

                    case = type(document.path, (TestCase, ), dict(
                        sybil=sybil, namespace=document.namespace,
                    ))

                    for example in document.examples():
                        suite.addTest(case(example))

        return suite

    return load_tests
