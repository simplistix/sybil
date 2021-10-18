from pytest import CaptureFixture

from .helpers import run_pytest, run_unittest


def test_pytest(capsys: CaptureFixture[str]):
    results = run_pytest(capsys, 'pytest')
    out = results.out

    # check we're trimming tracebacks:
    out.assert_not_present('sybil/example.py')

    out.then_find('fail.rst::line:1,column:1')
    out.then_find('fail.rst::line:1,column:1 sybil setup session_fixture setup\n'
                  'module_fixture setup\n'
                  'class_fixture setup\n'
                  'function_fixture setup\n'
                  'x is currently: 0\n'
                  'FAILED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('fail.rst::line:6,column:1')
    out.then_find('fail.rst::line:6,column:1 class_fixture setup\n'
                  'function_fixture setup\n'
                  '0smcf PASSED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('fail.rst::line:8,column:1')
    out.then_find('fail.rst::line:8,column:1 class_fixture setup\n'
                  'function_fixture setup\n'
                  '1smcf FAILED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('fail.rst::line:10,column:1')
    out.then_find('fail.rst::line:10,column:1 class_fixture setup\n'
                  'function_fixture setup\n'
                  '2smcf FAILED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('fail.rst::line:12,column:1')
    out.then_find('fail.rst::line:12,column:1 class_fixture setup\n'
                  'function_fixture setup\n'
                  '3smcf PASSED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('fail.rst::line:14,column:1')
    out.then_find('fail.rst::line:14,column:1 class_fixture setup\n'
                  'function_fixture setup\n'
                  'FAILED function_fixture teardown\n'
                  'class_fixture teardown\n'
                  'module_fixture teardown\n'
                  'sybil teardown 5')
    out.then_find('pass.rst::line:1,column:1')
    out.then_find('pass.rst::line:1,column:1 sybil setup module_fixture setup\n'
                  'class_fixture setup\n'
                  'function_fixture setup\n'
                  '0smcf PASSED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('pass.rst::line:3,column:1')
    out.then_find('pass.rst::line:3,column:1 class_fixture setup\n'
                  'function_fixture setup\n'
                  '1smcf PASSED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('pass.rst::line:5,column:1')
    out.then_find('pass.rst::line:5,column:1 class_fixture setup\n'
                  'function_fixture setup\n'
                  '2smcf PASSED function_fixture teardown\n'
                  'class_fixture teardown')
    out.then_find('pass.rst::line:7,column:1')
    out.then_find('pass.rst::line:7,column:1 class_fixture setup\n'
                  'function_fixture setup\n'
                  '3smcf PASSED function_fixture teardown\n'
                  'class_fixture teardown\n'
                  'module_fixture teardown\n'
                  'sybil teardown 4\n'
                  'session_fixture teardown')
    out.then_find('_ fail.rst line=1 column=1 _')
    out.then_find("raise Exception('the start!')")
    out.then_find('_ fail.rst line=8 column=1 _')
    out.then_find('Y count was 3 instead of 2')
    out.then_find('fail.rst:8: SybilFailure')
    out.then_find('_ fail.rst line=10 column=1 _')
    out.then_find('ValueError: X count was 3 instead of 4')
    out.then_find('_ fail.rst line=14 column=1 _')
    out.then_find("raise Exception('boom!')")
    out.then_find('fail.rst:18: Exception')

    assert results.return_code == 1
    assert results.failures == 4
    assert results.total == 10


def test_unittest(capsys: CaptureFixture[str]):
    results = run_unittest(capsys, 'unittest')
    out = results.out
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
    out.then_find('Ran 8 tests')

    assert results.total == 8
    assert results.failures == 1
    assert results.errors == 1
