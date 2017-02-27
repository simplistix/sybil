from unittest import TestCase, TestSuite


class Sybil(object):

    def __init__(self):
        class TestTest(TestCase):

            def test_one(sel):
                pass

            def test_two(sel):
                pass
        self.things = TestTest

    def unittest(self, loader, tests, pattern):
        suite = TestSuite()
        tests = loader.loadTestsFromTestCase(self.things)
        suite.addTests(tests)
        return suite


load_tests = Sybil().unittest
