import sys
from os.path import dirname, join
from unittest.main import main as unittest_main
from unittest.runner import TextTestRunner

from nose.core import run_exit as NoseMain, TextTestRunner as NoseRunner
from pytest import main as pytest_main

functional_test_dir = join(dirname(__file__), 'functional')


class Finder(object):

    def __init__(self, text):
        self.text = text
        self.index = 0

    def then_find(self, substring):
        assert substring in self.text[self.index:]
        self.index = self.text.index(substring, self.index)


def test_pytest(capsys):

    class CollectResults:
        def pytest_sessionfinish(self, session):
            self.session = session

    results = CollectResults()
    return_code = pytest_main(['-vvs', join(functional_test_dir, 'pytest')],
                              plugins=[results])
    assert return_code == 1
    assert results.session.testsfailed == 4
    assert results.session.testscollected == 10

    out, err = capsys.readouterr()
    # check we're trimming tracebacks:
    index = out.find('sybil/example.py')
    if index > -1:  # pragma: no cover
        raise AssertionError('\n'+out[index-500:index+500])

    out = Finder(out)
    out.then_find('fail.rst::line:1,column:1')
    out.then_find('fail.rst sybil setup session_fixture setup\n'
                  'module_fixture setup\n'
                  'class_fixture setup\n'
                  'function_fixture setup\n'
                  'x is currently: 0\n'
                  'FAILED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('fail.rst::line:6,column:1')
    out.then_find('fail.rst class_fixture setup\n'
                  'function_fixture setup\n'
                  '0smcf PASSED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('fail.rst::line:8,column:1')
    out.then_find('fail.rst class_fixture setup\n'
                  'function_fixture setup\n'
                  '1smcf FAILED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('fail.rst::line:10,column:1')
    out.then_find('fail.rst class_fixture setup\n'
                  'function_fixture setup\n'
                  '2smcf FAILED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('fail.rst::line:12,column:1')
    out.then_find('fail.rst class_fixture setup\n'
                  'function_fixture setup\n'
                  '3smcf PASSED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('fail.rst::line:14,column:1')
    out.then_find('fail.rst class_fixture setup\n'
                  'function_fixture setup\n'
                  'FAILED function_fixture teardown\n'
                  'class_fixture teardown\n'
                  'module_fixture teardown\n'
                  'sybil teardown 5')
    out.then_find('pass.rst::line:1,column:1')
    out.then_find('pass.rst sybil setup module_fixture setup\n'
                  'class_fixture setup\n'
                  'function_fixture setup\n'
                  '0smcf PASSED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('pass.rst::line:3,column:1')
    out.then_find('pass.rst class_fixture setup\n'
                  'function_fixture setup\n'
                  '1smcf PASSED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('pass.rst::line:5,column:1')
    out.then_find('pass.rst class_fixture setup\n'
                  'function_fixture setup\n'
                  '2smcf PASSED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('pass.rst::line:7,column:1')
    out.then_find('pass.rst class_fixture setup\n'
                  'function_fixture setup\n'
                  '3smcf PASSED function_fixture teardown\n'
                  'class_fixture teardown\n'
                  'module_fixture teardown\n'
                  'sybil teardown 4\n'
                  'session_fixture teardown')
    out.then_find('_ fail.rst line=1 column=1 _')
    out.then_find(  ">   raise Exception('the start!')")
    out.then_find('_ fail.rst line=8 column=1 _')
    out.then_find('Y count was 3 instead of 2')
    out.then_find('fail.rst:8: SybilFailure')
    out.then_find('_ fail.rst line=10 column=1 _')
    out.then_find('ValueError: X count was 3 instead of 4')
    out.then_find('_ fail.rst line=14 column=1 _')
    out.then_find(">       raise Exception('boom!')")
    out.then_find('fail.rst:18: Exception')


def common_checks(out):
    out.then_find('sybil setup')
    out.then_find('fail.rst,line:6,column:1 ... 0\nok')
    out.then_find('fail.rst,line:8,column:1 ... 1\nFAIL')
    out.then_find('fail.rst,line:10,column:1 ... 2\nERROR')
    out.then_find('fail.rst,line:12,column:1 ... 3\nok')
    out.then_find('sybil teardown 4\nsybil setup')
    out.then_find('pass.rst,line:1,column:1 ... 0\nok')
    out.then_find('pass.rst,line:3,column:1 ... 1\nok')
    out.then_find('pass.rst,line:5,column:1 ... 2\nok')
    out.then_find('pass.rst,line:7,column:1 ... 3\nok')
    out.then_find('sybil teardown 4')
    out.then_find('ERROR: ')
    out.then_find('fail.rst,line:10,column:1')
    out.then_find('ValueError: X count was 3 instead of 4')
    out.then_find('FAIL:')
    out.then_find('fail.rst,line:8,column:1')
    out.then_find('Y count was 3 instead of 2')


def test_unittest(capsys):
    runner = TextTestRunner(verbosity=2, stream=sys.stdout)
    path = join(functional_test_dir, 'functional_unittest')
    main = unittest_main(
        exit=False, module=None, testRunner=runner,
        argv=['x', 'discover', '-v', '-t', path, '-s', path]
    )
    out, err = capsys.readouterr()
    assert err == ''
    out = Finder(out)
    common_checks(out)
    out.then_find('Ran 8 tests')
    assert main.result.testsRun == 8
    assert len(main.result.failures) == 1
    assert len(main.result.errors) == 1


def test_nose(capsys):
    class ResultStoringMain(NoseMain):
        def runTests(self):
            self.testRunner = NoseRunner(stream=sys.stdout,
                                         verbosity=self.config.verbosity,
                                         config=self.config)
            self.result = self.testRunner.run(self.test)

    main = ResultStoringMain(
        module=None,
        argv=['x', '-vs', join(functional_test_dir, 'nose')]
    )
    assert main.result.testsRun == 9
    assert len(main.result.failures) == 1
    assert len(main.result.errors) == 1

    out, err = capsys.readouterr()
    assert err == ''
    out = Finder(out)
    common_checks(out)
