import sys

import pytest
from py.path import local
from pytest import CaptureFixture

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


def test_pytest(capsys: CaptureFixture[str]) -> None:
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


def test_unittest(capsys: CaptureFixture[str]) -> None:
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


def make_tree(tmpdir: local) -> None:
    write_doctest(tmpdir, 'foo.rst')
    write_doctest(tmpdir, 'bar.rst')
    write_doctest(tmpdir, 'parent', 'foo.rst')
    write_doctest(tmpdir, 'parent', 'bar.rst')
    write_doctest(tmpdir, 'parent', 'child', 'foo.rst')
    write_doctest(tmpdir, 'parent', 'child', 'bar.rst')


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_everything(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    make_tree(tmpdir)
    write_config(tmpdir, runner)
    results = run(capsys, runner, tmpdir)
    # ask for nothing, get nothing...
    assert results.total == 0


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_just_pattern(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    make_tree(tmpdir)
    write_config(tmpdir, runner, pattern="'*.rst'")
    results = run(capsys, runner, tmpdir)
    assert results.total == 6


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_fnmatch_pattern(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    make_tree(tmpdir)
    write_config(tmpdir, runner, pattern="'**/*.rst'")
    results = run(capsys, runner, tmpdir)
    # The fact that the two .rst files in the root aren't matched is
    # arguably a bug in the Python interpretation of **/
    results.out.assert_has_run(runner, '/parent/foo.rst')
    results.out.assert_has_run(runner, '/parent/bar.rst')
    results.out.assert_has_run(runner, '/parent/child/foo.rst')
    results.out.assert_has_run(runner, '/parent/child/bar.rst')
    assert results.total == 4, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_just_filenames(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    make_tree(tmpdir)
    write_config(tmpdir, runner,
                 filenames="['bar.rst']")
    results = run(capsys, runner, tmpdir)
    results.out.assert_has_run(runner, '/bar.rst')
    results.out.assert_has_run(runner, '/parent/bar.rst')
    results.out.assert_has_run(runner, '/parent/child/bar.rst')
    assert results.total == 3, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_directory(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    make_tree(tmpdir)
    write_config(tmpdir, runner,
                 path=f"'{tmpdir / 'parent'}'",
                 pattern="'*.rst'")
    results = run(capsys, runner, tmpdir)
    results.out.assert_has_run(runner, '/parent/foo.rst')
    results.out.assert_has_run(runner, '/parent/bar.rst')
    results.out.assert_has_run(runner, '/parent/child/foo.rst')
    results.out.assert_has_run(runner, '/parent/child/bar.rst')
    assert results.total == 4, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_directory_with_excludes(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    make_tree(tmpdir)
    write_config(tmpdir, runner,
                 path=f"'{tmpdir / 'parent'}'",
                 pattern="'*.rst'",
                 exclude="'ba*.rst'")
    results = run(capsys, runner, tmpdir)
    results.out.assert_has_run(runner, '/parent/foo.rst')
    results.out.assert_has_run(runner, '/parent/child/foo.rst')
    assert results.total == 2, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_filenames_and_excludes(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    make_tree(tmpdir)
    write_config(tmpdir, runner,
                 path=f"'{tmpdir / 'parent'}'",
                 filenames="{'bar.rst'}",
                 excludes="['**child/*.rst']")
    results = run(capsys, runner, tmpdir)
    results.out.assert_has_run(runner, '/parent/bar.rst')
    assert results.total == 1, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_exclude_by_name(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    write_doctest(tmpdir, 'foo.txt')
    write_doctest(tmpdir, 'bar.txt')
    write_doctest(tmpdir, 'child', 'foo.txt')
    write_doctest(tmpdir, 'child', 'bar.txt')
    write_config(tmpdir, runner,
                 pattern="'*.txt'",
                 exclude="'bar.txt'")
    results = run(capsys, runner, tmpdir)
    results.out.assert_has_run(runner, '/foo.txt')
    results.out.assert_has_run(runner, '/child/foo.txt')
    assert results.total == 2, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_include_filenames(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    write_doctest(tmpdir, 'foo.txt')
    write_doctest(tmpdir, 'bar.txt')
    write_doctest(tmpdir, 'baz', 'bar.txt')
    write_config(tmpdir, runner,
                 filenames="['bar.txt']")
    results = run(capsys, runner, tmpdir)
    results.out.assert_has_run(runner, '/bar.txt')
    results.out.assert_has_run(runner, '/baz/bar.txt')
    assert results.total == 2, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_globs(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    write_doctest(tmpdir, 'middle', 'interesting', 'foo.txt')
    write_doctest(tmpdir, 'middle', 'boring', 'bad1.txt')
    write_doctest(tmpdir, 'middle', 'boring', 'bad2.txt')
    write_config(tmpdir, runner,
                 patterns="['middle/**/*.txt']",
                 excludes="['**/boring/*.txt']")
    results = run(capsys, runner, tmpdir)
    results.out.assert_has_run(runner, '/middle/interesting/foo.txt')
    assert results.total == 1, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_multiple_patterns(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    write_doctest(tmpdir, 'test.rst')
    write_doctest(tmpdir, 'test.txt')
    write_config(tmpdir, runner,
                 patterns="['*.rst', '*.txt']")
    results = run(capsys, runner, tmpdir)
    assert results.total == 2, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_skips(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    root = clone_functional_sample('skips', tmpdir)
    write_config(root, runner,
                 parsers="[PythonCodeBlockParser(), SkipParser(), DocTestParser()]",
                 patterns="['*.rst']")
    results = run(capsys, runner, root)
    assert results.total == 10, results.out.text
    assert results.failures == 0, results.out.text
    assert results.errors == 0, results.out.text


def clone_and_run_modules_tests(tmpdir: local, capsys: CaptureFixture[str], runner: str):
    clone_functional_sample('modules', tmpdir)
    write_config(tmpdir, runner,
                 path="'./modules'",
                 parsers="[PythonCodeBlockParser(), DocTestParser()]",
                 patterns="['*.py']")
    results = run(capsys, runner, tmpdir)
    return results


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_modules(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    sys.path.append((tmpdir / 'modules').strpath)
    results = clone_and_run_modules_tests(tmpdir, capsys, runner)
    assert results.total == 5, results.out.text
    assert results.failures == 0, results.out.text
    assert results.errors == 0, results.out.text


def test_modules_not_importable_pytest(tmpdir: local, capsys: CaptureFixture[str]) -> None:
    # NB: no append to sys.path
    results = clone_and_run_modules_tests(tmpdir, capsys, PYTEST)
    assert results.total == 5, results.out.text
    assert results.failures == 5, results.out.text
    assert results.errors == 0, results.out.text
    out = results.out
    out.then_find('a.py line=3 column=1')
    out.then_find(f"ImportError: 'a' not importable from {tmpdir/'modules'/'a.py'} as:")
    out.then_find("ModuleNotFoundError: No module named 'a'")
    out.then_find('b.py line=7 column=1')
    out.then_find(f"ImportError: 'b' not importable from {tmpdir/'modules'/'b.py'} as:")
    out.then_find("ModuleNotFoundError: No module named 'b'")


def test_modules_not_importable_unittest(tmpdir: local, capsys: CaptureFixture[str]) -> None:
    # NB: no append to sys.path
    results = clone_and_run_modules_tests(tmpdir, capsys, UNITTEST)
    assert results.total == 5, results.out.text
    assert results.failures == 0, results.out.text
    assert results.errors == 5, results.out.text
    a_py = tmpdir/'modules'/'a.py'
    b_py = tmpdir/'modules'/'b.py'
    out = results.out
    out.then_find(f'ERROR: {a_py},line:3,column:1')
    out.then_find(f"ImportError: 'a' not importable from {tmpdir/'modules'/'a.py'} as:")
    out.then_find("ModuleNotFoundError: No module named 'a'")
    out.then_find(f'ERROR: {b_py},line:2,column:1')
    out.then_find(f"ImportError: 'b' not importable from {tmpdir/'modules'/'b.py'} as:")
    out.then_find("ModuleNotFoundError: No module named 'b'")


@skip_if_37_or_older()
@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_package_and_docs(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    root = clone_functional_sample('package_and_docs', tmpdir)
    write_config(root, runner,
                 patterns="['**/*.py', '**/*.rst']")
    sys.path.append((root / 'src').strpath)
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
def test_multiple_sybils_process_all(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    write_doctest(tmpdir, 'test.rst')
    write_doctest(tmpdir, 'test.txt')
    config_template = """
    from sybil.parsers.rest import DocTestParser
    from sybil import Sybil
    
    sybil1 = Sybil(parsers=[DocTestParser()], pattern='test.*')
    sybil2 = Sybil(parsers=[DocTestParser()], pattern='test.*')
    
    {assigned_name} = (sybil1 + sybil2).{integration}()
    """
    write_config(tmpdir, runner, template=config_template)
    results = run(capsys, runner, tmpdir)
    if runner == PYTEST:
        # the pytest integration only looks at each file once
        expected_total = 2
    else:
        expected_total = 4
    assert results.total == expected_total, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_multiple_sybils_process_one_each(tmpdir: local, capsys: CaptureFixture[str], runner: str) -> None:
    write_doctest(tmpdir, 'test.rst')
    write_doctest(tmpdir, 'test.txt')
    config_template = """
    from sybil.parsers.rest import DocTestParser
    from sybil import Sybil

    rst = Sybil(parsers=[DocTestParser()], pattern='*.rst')
    txt = Sybil(parsers=[DocTestParser()], pattern='*.txt')

    {assigned_name} = (rst + txt).{integration}()
    """
    write_config(tmpdir, runner, template=config_template)
    results = run(capsys, runner, tmpdir)
    assert results.total == 2, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_myst(capsys: CaptureFixture[str], runner: str) -> None:
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

@skip_if_37_or_older()
def test_codeblock_with_protocol_then_doctest() -> None:
    sybil = Sybil([PythonCodeBlockParser(), DocTestParser()])
    check_path(sample_path('protocol-typing.rst'), sybil, expected=3)
