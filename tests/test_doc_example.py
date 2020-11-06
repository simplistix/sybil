import sys
from os import pardir
from os.path import dirname, join
from unittest.main import main as unittest_main
from unittest.runner import TextTestRunner
from pytest import main as pytest_main

example_dir = join(dirname(__file__), pardir, 'docs', 'example')


def test_pytest(capsys):

    class CollectResults:
        def pytest_sessionfinish(self, session):
            self.session = session

    results = CollectResults()
    return_code = pytest_main([join(example_dir, 'docs')],
                              plugins=[results])
    assert return_code == 0
    assert results.session.testsfailed == 0
    assert results.session.testscollected == 3


def test_unittest(capsys):
    runner = TextTestRunner(verbosity=2, stream=sys.stdout)
    path = join(example_dir, 'example_unittest')
    main = unittest_main(
        exit=False, module=None, testRunner=runner,
        argv=['x', 'discover', '-s', path, '-t', path]
    )
    assert main.result.testsRun == 3
    assert len(main.result.failures) == 0
    assert len(main.result.errors) == 0
