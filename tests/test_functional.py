import sys
from pathlib import Path

import pytest
from pytest import CaptureFixture
from testfixtures import compare

from sybil import Sybil
from sybil.parsers.rest import PythonCodeBlockParser, DocTestParser
from sybil.python import import_cleanup
from .helpers import (
    run_pytest, run_unittest, PYTEST, run, write_config, UNITTEST, write_doctest,
    functional_sample, clone_functional_sample, skip_if_37_or_older, check_path, sample_path
)


@pytest.fixture(autouse=True)
def cleanup_imports():
    with import_cleanup():
        yield


def test_pytest(capsys: CaptureFixture[str]):
    results = run_pytest(capsys, functional_sample('pytest'))
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
    results = run_unittest(capsys, functional_sample('unittest'))
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


def make_tree(tmp_path: Path):
    write_doctest(tmp_path, 'foo.rst')
    write_doctest(tmp_path, 'bar.rst')
    write_doctest(tmp_path, 'parent', 'foo.rst')
    write_doctest(tmp_path, 'parent', 'bar.rst')
    write_doctest(tmp_path, 'parent', 'child', 'foo.rst')
    write_doctest(tmp_path, 'parent', 'child', 'bar.rst')


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_everything(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    make_tree(tmp_path)
    write_config(tmp_path, runner)
    results = run(capsys, runner, tmp_path)
    # ask for nothing, get nothing...
    assert results.total == 0


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_just_pattern(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    make_tree(tmp_path)
    write_config(tmp_path, runner, pattern="'*.rst'")
    results = run(capsys, runner, tmp_path)
    assert results.total == 6


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_fnmatch_pattern(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    make_tree(tmp_path)
    write_config(tmp_path, runner, pattern="'**/*.rst'")
    results = run(capsys, runner, tmp_path)
    # The fact that the two .rst files in the root aren't matched is
    # arguably a bug in the Python interpretation of **/
    results.out.assert_has_run(runner, '/parent/foo.rst')
    results.out.assert_has_run(runner, '/parent/bar.rst')
    results.out.assert_has_run(runner, '/parent/child/foo.rst')
    results.out.assert_has_run(runner, '/parent/child/bar.rst')
    assert results.total == 4, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_just_filenames(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    make_tree(tmp_path)
    write_config(tmp_path, runner,
                 filenames="['bar.rst']")
    results = run(capsys, runner, tmp_path)
    results.out.assert_has_run(runner, '/bar.rst')
    results.out.assert_has_run(runner, '/parent/bar.rst')
    results.out.assert_has_run(runner, '/parent/child/bar.rst')
    assert results.total == 3, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_directory(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    make_tree(tmp_path)
    write_config(tmp_path, runner,
                 path=f"'{tmp_path / 'parent'}'",
                 pattern="'*.rst'")
    results = run(capsys, runner, tmp_path)
    results.out.assert_has_run(runner, '/parent/foo.rst')
    results.out.assert_has_run(runner, '/parent/bar.rst')
    results.out.assert_has_run(runner, '/parent/child/foo.rst')
    results.out.assert_has_run(runner, '/parent/child/bar.rst')
    assert results.total == 4, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_directory_with_excludes(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    make_tree(tmp_path)
    write_config(tmp_path, runner,
                 path=f"'{tmp_path / 'parent'}'",
                 pattern="'*.rst'",
                 exclude="'ba*.rst'")
    results = run(capsys, runner, tmp_path)
    results.out.assert_has_run(runner, '/parent/foo.rst')
    results.out.assert_has_run(runner, '/parent/child/foo.rst')
    assert results.total == 2, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_filenames_and_excludes(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    make_tree(tmp_path)
    write_config(tmp_path, runner,
                 path=f"'{tmp_path / 'parent'}'",
                 filenames="{'bar.rst'}",
                 excludes="['**child/*.rst']")
    results = run(capsys, runner, tmp_path)
    results.out.assert_has_run(runner, '/parent/bar.rst')
    assert results.total == 1, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_exclude_by_name(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    write_doctest(tmp_path, 'foo.txt')
    write_doctest(tmp_path, 'bar.txt')
    write_doctest(tmp_path, 'child', 'foo.txt')
    write_doctest(tmp_path, 'child', 'bar.txt')
    write_config(tmp_path, runner,
                 pattern="'*.txt'",
                 exclude="'bar.txt'")
    results = run(capsys, runner, tmp_path)
    results.out.assert_has_run(runner, '/foo.txt')
    results.out.assert_has_run(runner, '/child/foo.txt')
    assert results.total == 2, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_include_filenames(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    write_doctest(tmp_path, 'foo.txt')
    write_doctest(tmp_path, 'bar.txt')
    write_doctest(tmp_path, 'baz', 'bar.txt')
    write_config(tmp_path, runner,
                 filenames="['bar.txt']")
    results = run(capsys, runner, tmp_path)
    results.out.assert_has_run(runner, '/bar.txt')
    results.out.assert_has_run(runner, '/baz/bar.txt')
    assert results.total == 2, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_globs(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    write_doctest(tmp_path, 'middle', 'interesting', 'foo.txt')
    write_doctest(tmp_path, 'middle', 'boring', 'bad1.txt')
    write_doctest(tmp_path, 'middle', 'boring', 'bad2.txt')
    write_config(tmp_path, runner,
                 patterns="['middle/**/*.txt']",
                 excludes="['**/boring/*.txt']")
    results = run(capsys, runner, tmp_path)
    results.out.assert_has_run(runner, '/middle/interesting/foo.txt')
    assert results.total == 1, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_multiple_patterns(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    write_doctest(tmp_path, 'test.rst')
    write_doctest(tmp_path, 'test.txt')
    write_config(tmp_path, runner,
                 patterns="['*.rst', '*.txt']")
    results = run(capsys, runner, tmp_path)
    assert results.total == 2, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_skips(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    root = clone_functional_sample('skips', tmp_path)
    write_config(root, runner,
                 parsers="[PythonCodeBlockParser(), SkipParser(), DocTestParser()]",
                 patterns="['*.rst']")
    results = run(capsys, runner, root)
    assert results.total == 10, results.out.text
    assert results.failures == 0, results.out.text
    assert results.errors == 0, results.out.text


def clone_and_run_modules_tests(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    clone_functional_sample('modules', tmp_path)
    write_config(tmp_path, runner,
                 path="'./modules'",
                 parsers="[PythonCodeBlockParser(), DocTestParser()]",
                 patterns="['*.py']")
    results = run(capsys, runner, tmp_path)
    return results


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_modules(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    sys.path.append(str(tmp_path / 'modules'))
    results = clone_and_run_modules_tests(tmp_path, capsys, runner)
    assert results.total == 5, results.out.text
    assert results.failures == 0, results.out.text
    assert results.errors == 0, results.out.text


def test_modules_not_importable_pytest(tmp_path: Path, capsys: CaptureFixture[str]):
    # NB: no append to sys.path
    results = clone_and_run_modules_tests(tmp_path, capsys, PYTEST)
    compare(results.total, expected=5, suffix=results.out.text)
    compare(results.errors, expected=0, suffix=results.out.text)
    compare(results.failures, expected=5, suffix=results.out.text)
    out = results.out
    out.then_find('a.py line=3 column=1')
    out.then_find(f"ImportError: 'a' not importable from {tmp_path/'modules'/'a.py'} as:")
    out.then_find("ModuleNotFoundError: No module named 'a'")
    out.then_find('a.py line=7 column=1')
    out.then_find("ModuleNotFoundError: No module named 'a'")
    out.then_find('b.py line=2 column=1')
    out.then_find(f"ImportError: 'b' not importable from {tmp_path/'modules'/'b.py'} as:")
    out.then_find('b.py line=7 column=1')
    out.then_find("ModuleNotFoundError: No module named 'b'")
    out.then_find('b.py line=11 column=1')
    out.then_find("ModuleNotFoundError: No module named 'b'")


def test_modules_not_importable_unittest(tmp_path: Path, capsys: CaptureFixture[str]):
    # NB: no append to sys.path
    results = clone_and_run_modules_tests(tmp_path, capsys, UNITTEST)
    assert results.total == 5, results.out.text
    assert results.failures == 0, results.out.text
    assert results.errors == 5, results.out.text
    a_py = tmp_path/'modules'/'a.py'
    b_py = tmp_path/'modules'/'b.py'
    out = results.out
    out.then_find(f'ERROR: {a_py},line:3,column:1')
    out.then_find(f"ImportError: 'a' not importable from {tmp_path/'modules'/'a.py'} as:")
    out.then_find("ModuleNotFoundError: No module named 'a'")
    out.then_find(f'ERROR: {b_py},line:2,column:1')
    out.then_find(f"ImportError: 'b' not importable from {tmp_path/'modules'/'b.py'} as:")
    out.then_find("ModuleNotFoundError: No module named 'b'")


@skip_if_37_or_older()
@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_package_and_docs(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    root = clone_functional_sample('package_and_docs', tmp_path)
    write_config(root, runner,
                 patterns="['**/*.py', '**/*.rst']")
    sys.path.append(str((root / 'src')))
    results = run(capsys, runner, root)
    assert results.total == 7, results.out.text
    assert results.failures == 1, results.out.text
    assert results.errors == 0, results.out.text
    # output from the one expected failure!
    results.out.then_find('Expected:')
    results.out.then_find('good')
    results.out.then_find('Got:')
    results.out.then_find('bad')


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_multiple_sybils_process_all(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    write_doctest(tmp_path, 'test.rst')
    write_doctest(tmp_path, 'test.txt')
    config_template = """
    from sybil.parsers.rest import DocTestParser
    from sybil import Sybil
    
    sybil1 = Sybil(parsers=[DocTestParser()], pattern='test.*')
    sybil2 = Sybil(parsers=[DocTestParser()], pattern='test.*')
    
    {assigned_name} = (sybil1 + sybil2).{integration}()
    """
    write_config(tmp_path, runner, template=config_template)
    results = run(capsys, runner, tmp_path)
    if runner == PYTEST:
        # the pytest integration only looks at each file once
        expected_total = 2
    else:
        expected_total = 4
    assert results.total == expected_total, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_multiple_sybils_process_one_each(tmp_path: Path, capsys: CaptureFixture[str], runner: str):
    write_doctest(tmp_path, 'test.rst')
    write_doctest(tmp_path, 'test.txt')
    config_template = """
    from sybil.parsers.rest import DocTestParser
    from sybil import Sybil

    rst = Sybil(parsers=[DocTestParser()], pattern='*.rst')
    txt = Sybil(parsers=[DocTestParser()], pattern='*.txt')

    {assigned_name} = (rst + txt).{integration}()
    """
    write_config(tmp_path, runner, template=config_template)
    results = run(capsys, runner, tmp_path)
    assert results.total == 2, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_myst(capsys: CaptureFixture[str], runner: str):
    results = run(capsys, runner, functional_sample('myst'))
    out = results.out

    # Check all the tests are found:
    out.assert_has_run(runner, '/doctest.md', line=7)
    out.assert_has_run(runner, '/doctest.md', line=14)
    out.assert_has_run(runner, '/doctest.md', line=25)
    out.assert_has_run(runner, '/doctest.md', line=31)
    out.assert_has_run(runner, '/python.md', line=5)
    out.assert_has_run(runner, '/python.md', line=11)
    out.assert_has_run(runner, '/python.md', line=17)
    out.assert_has_run(runner, '/python.md', line=26)
    out.assert_has_run(runner, '/python.md', line=41)
    out.assert_has_run(runner, '/python.md', line=47)
    out.assert_has_run(runner, '/python.md', line=49)

    # unittest treats exceptions as errors rather than failures,
    # and they appear at the top of the output, hence the conditionals below.

    # Check counts:
    assert results.total == 4+7, results.out.text
    if runner == PYTEST:
        assert results.failures == 2 + 1, results.out.text
        assert results.errors == 0, results.out.text
    else:
        assert results.failures == 2 + 0, results.out.text
        assert results.errors == 1, results.out.text

    # Check error text:
    if runner == UNITTEST:
        out.then_find("Exception: boom!")
    out.then_find("doctest.md, line 25, column 1 did not evaluate as expected:")
    out.then_find("Expected:\n    3\nGot:\n    2\n")
    out.then_find("doctest.md, line 31, column 1 did not evaluate as expected:")
    out.then_find("Expected:\n    4\nGot:\n    2\n")
    if runner == PYTEST:
        out.then_find("Exception: boom!")


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_markdown(capsys: CaptureFixture[str], runner: str):
    results = run(capsys, runner, functional_sample('markdown'))
    out = results.out

    # Check all the tests are found:
    out.assert_has_run(runner, '/doctest.md', line=7)
    out.assert_has_run(runner, '/python.md', line=5)
    out.assert_has_run(runner, '/python.md', line=11)
    out.assert_has_run(runner, '/python.md', line=26)
    out.assert_has_run(runner, '/python.md', line=32)
    out.assert_has_run(runner, '/python.md', line=34)

    # unittest treats exceptions as errors rather than failures,
    # and they appear at the top of the output, hence the conditionals below.

    # Check counts:
    assert results.total == 1+5, results.out.text
    if runner == PYTEST:
        assert results.failures == 0 + 1, results.out.text
        assert results.errors == 0, results.out.text
    else:
        assert results.failures == 0 + 0, results.out.text
        assert results.errors == 1, results.out.text

    # Check error text:
    out.then_find("Exception: boom!")


@skip_if_37_or_older()
def test_codeblock_with_protocol_then_doctest():
    sybil = Sybil([PythonCodeBlockParser(), DocTestParser()])
    check_path(sample_path('protocol-typing.rst'), sybil, expected=3)
