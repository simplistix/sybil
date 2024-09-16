Test runner integration
=======================

Sybil aims to integrate with all major Python test runners. Those currently
catered for explicitly are listed below, but you may find that one of these
integration methods will work as required with other test runners.
If not, please file an issue on GitHub.

To show how the integration options work, the following documentation examples
will be tested. They use :ref:`doctests <doctest-simple-testfile>`,
:rst:dir:`code blocks <code-block>` and require a temporary directory:

.. literalinclude:: examples/integration/docs/example.rst
  :language: rest

.. _pytest_integration:

pytest
~~~~~~

You should install Sybil with the ``pytest`` extra, to ensure
you have a compatible version of `pytest`__:

__ https://docs.pytest.org

.. code-block:: bash

  pip install sybil[pytest]

To have `pytest`__ check the examples, Sybil makes use of the
``pytest_collect_file`` hook. To use this, configuration is placed in
a ``confest.py`` in your documentation source directory, as shown below.
``pytest`` should be invoked from a location that has the opportunity to
recurse into that directory:

__ https://docs.pytest.org

.. literalinclude:: examples/integration/docs/conftest.py

The file glob passed as ``pattern`` should match any documentation source
files that contain examples which you would like to be checked.

As you can see, if your examples require any fixtures, these can be requested
by passing their names to the ``fixtures`` argument of the
:class:`~sybil.Sybil` class.
These will be available in the :class:`~sybil.Document`
:class:`~sybil.Document.namespace` in a way that should feel natural
to ``pytest`` users.

The ``setup`` and ``teardown`` parameters can still be used to pass
:class:`~sybil.Document` setup and teardown callables.

The ``path`` parameter, however, is ignored.


.. note::

    pytest provides its own doctest plugin, which can cause problems. It
    should be disabled by including the following in your pytest configuration file:

    .. literalinclude:: examples/quickstart/pytest.ini
        :language: ini

.. _unitttest_integration:

unittest
~~~~~~~~

To have :ref:`unittest-test-discovery` check the example, Sybil makes use of
the `load_tests protocol`__. As such, the following should be placed in a test
module, say ``test_docs.py``, where the unit test discovery process can find it:

__ https://docs.python.org/3/library/unittest.html#load-tests-protocol

.. literalinclude:: examples/integration/unittest/test_docs.py

The ``path`` parameter gives the path, relative to the file containing this
code, that contains the documentation source files.

The file glob passed as ``pattern`` should match any documentation source
files that contain examples which you would like to be checked.

Any setup or teardown necessary for your tests can be carried out in
callables passed to the ``setup`` and ``teardown`` parameters,
which are both called with the :class:`~sybil.Document`
:class:`~sybil.Document.namespace`.

The ``fixtures`` parameter is ignored.
