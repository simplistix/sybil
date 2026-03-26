from unittest.mock import Mock

import pytest
from _pytest.config import PytestPluginManager
from sybil import Sybil
from sybil.testing import check_sybil, check_lexer, run_pytest
from testfixtures import ShouldAssert, ShouldRaise, replace_on_class


class TestCheckSybil:
    def test_no_matches(self):
        with ShouldAssert("Expected exactly one example, got: []"):
            check_sybil(Sybil([]), "")


class TestCheckLexer:
    def test_no_matches(self):
        with ShouldAssert("Expected exactly one region, got: []"):
            check_lexer(lambda _: [], "", expected_text="", expected_lexemes={})


class TestRunPytest:
    def test_passing_test_no_fixtures(self):
        def test_simple():
            assert 1 + 1 == 2

        run_pytest(test_simple)

    def test_passing_test_with_fixture(self):
        @pytest.fixture()
        def my_value():
            return 42

        def test_with_fixture(my_value):
            assert my_value == 42

        run_pytest(test_with_fixture, fixtures=[my_value])

    def test_passing_test_with_yield_fixture(self):
        @pytest.fixture()
        def my_value():
            yield 99

        def test_with_yield(my_value):
            assert my_value == 99

        run_pytest(test_with_yield, fixtures=[my_value])

    def test_failing_test(self):
        def test_fails():
            assert False, "intentional failure"

        with ShouldAssert(
            'Expected 0 test(s) to fail, but 1 did:\n\n'
            'tests/test_testing.py:51: in test_fails\n'
            '    assert False, "intentional failure"\n'
            'E   AssertionError: intentional failure\n'
            'E   assert False'
        ):
            run_pytest(test_fails)

    def test_expected_failures(self):
        def test_fails():
            assert False, "intentional failure"

        run_pytest(test_fails, expected_failed=1)

    def test_expected_failures_but_none_occur(self):
        def test_passes():
            pass

        with ShouldAssert("Expected 1 test(s) to fail, but none did"):
            run_pytest(test_passes, expected_failed=1)

    def test_builtin_fixture(self):
        def test_with_tmp_path(tmp_path):
            assert tmp_path.exists()

        run_pytest(test_with_tmp_path)

    def test_multiple_tests(self):
        def test_a():
            pass

        def test_b():
            assert 1 == 1

        run_pytest(test_a, test_b)

    def test_fixtures_as_sequence(self):
        @pytest.fixture()
        def value_a():
            return 1

        @pytest.fixture()
        def value_b():
            return 2

        def test_both(value_a, value_b):
            assert value_a + value_b == 3

        run_pytest(test_both, fixtures=[value_a, value_b])

    def test_outer_session_plugins_not_re_invoked(self):
        load_setuptools_entrypoints = Mock()

        def test_simple():
            pass

        with replace_on_class(
            PytestPluginManager.load_setuptools_entrypoints, load_setuptools_entrypoints
        ):
            run_pytest(test_simple)

        load_setuptools_entrypoints.assert_not_called()

    def test_fixture_not_requested(self):
        @pytest.fixture()
        def value_a():
            return 1

        def test_both(value_a, value_b): ...

        with ShouldRaise(AssertionError, match=r"fixture 'value_b' not found"):
            run_pytest(test_both, fixtures=[value_a])
