import sys
from os.path import join
from pathlib import Path
from unittest.main import main as unittest_main
from unittest.runner import TextTestRunner

import pytest
from pytest import main as pytest_main

from tests.helpers import add_to_python_path

DOC_EXAMPLES = Path(__file__).parent.parent / 'docs' / 'examples'


class CollectResults:
    def pytest_sessionfinish(self, session):
        self.session = session


def pytest_in(*path: str):
    results = CollectResults()
    return_code = pytest_main([join(DOC_EXAMPLES, *path)], plugins=[results])
    assert return_code == results.session.exitstatus
    return results.session


class TestIntegrationExamples:

    def test_pytest(self):
        session = pytest_in('integration', 'docs')
        assert session.exitstatus == 0
        assert session.testsfailed == 0
        assert session.testscollected == 3

    def test_unittest(self):
        runner = TextTestRunner(verbosity=2, stream=sys.stdout)
        path = str(DOC_EXAMPLES / 'integration' / 'unittest')
        main = unittest_main(
            exit=False, module=None, testRunner=runner,
            argv=['x', 'discover', '-s', path, '-t', path]
        )
        assert main.result.testsRun == 3
        assert len(main.result.failures) == 0
        assert len(main.result.errors) == 0


def test_quickstart():
    session = pytest_in('quickstart')
    assert session.exitstatus == 0
    assert session.testsfailed == 0
    assert session.testscollected == 4


def test_rest_text_rest_src():
    directory = 'rest_text_rest_src'
    with add_to_python_path(DOC_EXAMPLES / directory / 'src'):
        session = pytest_in(directory)
    assert session.testsfailed == 0
    assert session.testscollected == 5


def test_myst_text_rest_src():
    directory = 'myst_text_rest_src'
    with add_to_python_path(DOC_EXAMPLES / directory / 'src'):
        session = pytest_in(directory)
    assert session.testsfailed == 0
    assert session.testscollected == 5
