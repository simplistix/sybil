import pytest
from py.path import local
from pytest import CaptureFixture

from sybil.python import import_cleanup
from .helpers import (
    run_pytest, run_unittest, PYTEST, run, write_config, UNITTEST, write_doctest,
    functional_sample, clone_functional_sample
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


def make_tree(tmpdir: local) -> None:
    write_doctest(tmpdir, 'foo.rst')
    write_doctest(tmpdir, 'bar.rst')
    write_doctest(tmpdir, 'parent', 'foo.rst')
    write_doctest(tmpdir, 'parent', 'bar.rst')
    write_doctest(tmpdir, 'parent', 'child', 'foo.rst')
    write_doctest(tmpdir, 'parent', 'child', 'bar.rst')


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_everything(tmpdir: local, capsys: CaptureFixture[str], runner: str):
    make_tree(tmpdir)
    write_config(tmpdir, runner)
    results = run(capsys, runner, tmpdir)
    # ask for nothing, get nothing...
    assert results.total == 0


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_just_pattern(tmpdir: local, capsys: CaptureFixture[str], runner: str):
    make_tree(tmpdir)
    write_config(tmpdir, runner, pattern="'*.rst'")
    results = run(capsys, runner, tmpdir)
    assert results.total == 6


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_fnmatch_pattern(tmpdir: local, capsys: CaptureFixture[str], runner: str):
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
def test_filter_just_filenames(tmpdir: local, capsys: CaptureFixture[str], runner: str):
    make_tree(tmpdir)
    write_config(tmpdir, runner,
                 filenames="['bar.rst']")
    results = run(capsys, runner, tmpdir)
    results.out.assert_has_run(runner, '/bar.rst')
    results.out.assert_has_run(runner, '/parent/bar.rst')
    results.out.assert_has_run(runner, '/parent/child/bar.rst')
    assert results.total == 3, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_directory(tmpdir: local, capsys: CaptureFixture[str], runner: str):
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
def test_filter_directory_with_excludes(tmpdir: local, capsys: CaptureFixture[str], runner: str):
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
def test_filter_filenames_and_excludes(tmpdir: local, capsys: CaptureFixture[str], runner: str):
    make_tree(tmpdir)
    write_config(tmpdir, runner,
                 path=f"'{tmpdir / 'parent'}'",
                 filenames="{'bar.rst'}",
                 excludes="['**child/*.rst']")
    results = run(capsys, runner, tmpdir)
    results.out.assert_has_run(runner, '/parent/bar.rst')
    assert results.total == 1, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_filter_exclude_by_name(tmpdir: local, capsys: CaptureFixture[str], runner: str):
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
def test_filter_include_filenames(tmpdir: local, capsys: CaptureFixture[str], runner: str):
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
def test_filter_globs(tmpdir: local, capsys: CaptureFixture[str], runner: str):
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
def test_filter_multiple_patterns(tmpdir: local, capsys: CaptureFixture[str], runner: str):
    write_doctest(tmpdir, 'test.rst')
    write_doctest(tmpdir, 'test.txt')
    write_config(tmpdir, runner,
                 patterns="['*.rst', '*.txt']")
    results = run(capsys, runner, tmpdir)
    assert results.total == 2, results.out.text


@pytest.mark.parametrize('runner', [PYTEST, UNITTEST])
def test_skips(tmpdir: local, capsys: CaptureFixture[str], runner: str):
    root = clone_functional_sample('skips', tmpdir)
    write_config(root, runner,
                 parsers="[PythonCodeBlockParser(), skip, DocTestParser()]",
                 patterns="['*.rst']")
    results = run(capsys, runner, root)
    assert results.total == 10, results.out.text
    assert results.failures == 0, results.out.text
    assert results.errors == 0, results.out.text
