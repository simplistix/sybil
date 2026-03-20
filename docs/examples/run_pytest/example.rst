Here's an example fixture and test:

.. code-block:: python

  from contextlib import contextmanager
  from collections.abc import Iterator
  from unittest.mock import Mock, call
  import pytest

  @contextmanager
  def my_context_manager() -> Iterator[Mock]:
      mock = Mock()
      try:
          yield mock
      finally:
          mock.done = True

  @pytest.fixture()
  def my_mock() -> Iterator[Mock]:
      with my_context_manager() as mock_:
          yield mock_


  def test_things(my_mock: Mock) -> None:
      my_mock.fake_method()
      assert my_mock.fake_method.call_count == 1

.. invisible-code-block: python

  from sybil.testing import run_pytest
  run_pytest(test_things, fixtures=[my_mock])
