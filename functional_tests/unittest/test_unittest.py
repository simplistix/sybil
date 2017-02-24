from unittest import TestCase, TestSuite


class TestTest(TestCase):

    def test_one(sel):
        pass

    def test_two(sel):
        pass


def load_tests(loader, tests, pattern):
    suite = TestSuite()
    tests = loader.loadTestsFromTestCase(TestTest)
    suite.addTests(tests)
    return suite
