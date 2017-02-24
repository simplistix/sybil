from os.path import split, join
from nose.core import run_exit as NoseMain, TextTestRunner as NoseRunner
from pytest import main as pytest_main
from unittest.main import main as unittest_main

functional_test_dir = join(*(split(__file__)[:-2]+('functional_tests', )))


def test_pytest():

    class CollectResults:
        def pytest_sessionfinish(self, session):
            self.session = session

    results = CollectResults()
    return_code = pytest_main(['-qq', join(functional_test_dir, 'pytest')],
                              plugins=[results])
    assert return_code == 0
    assert results.session.testsfailed == 0
    assert results.session.testscollected == 1


def test_unittest():
    main = unittest_main(
        exit=False, module=None,
        argv=['x', 'discover', '-s', join(functional_test_dir, 'unittest')]
    )
    assert main.result.testsRun == 2
    assert main.result.failures == []


def test_nose():
    class ResultStoringMain(NoseMain):
        def runTests(self):
            self.testRunner = NoseRunner(stream=self.config.stream,
                                         verbosity=self.config.verbosity,
                                         config=self.config)
            self.result = self.testRunner.run(self.test)

    main = ResultStoringMain(
        module=None,
        argv=['x', join(functional_test_dir, 'nose')]
    )
    assert main.result.testsRun == 3
    assert main.result.failures == []
