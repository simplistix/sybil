Usage
=====

As a quick-start, here's how you would set up a ``conftest.py`` in the root of your
project such that running `pytest`__ would check examples in your project's source code
and `Sphinx`__ source. :ref:`doctest <doctest-simple-testfile>` and Python
:rst:dir:`code-block` examples will be checked:

.. literalinclude:: ../conftest.py
   :lines: 1-5, 7-11, 14-

__ https://docs.pytest.org
__ http://www.sphinx-doc.org/

You'll also want to disable pytest's own doctest plugin by putting this in your pytest config:

.. literalinclude:: example/pytest.ini
   :lines: 2

An example of a documentation source file that could be checked using the above
configuration is shown below:

.. literalinclude:: example.rst
  :language: rest

Method of operation
-------------------

:class:`~sybil.Sybil` works by discovering a series of
:class:`documents <sybil.Document>` as part of the
:ref:`test runner integration <integrations>`. These documents are then
:doc:`parsed <parsers>` into a set of non-overlapping
:class:`regions <sybil.Region>`. When the tests are run, each :class:`~sybil.Region`
is turned into an :class:`~sybil.Example` that is evaluated in the document's
:class:`~sybil.Document.namespace`. The examples are evaluated
in the order in which they appear in the document.
If an example does not evaluate as expected, a test failure occurs and Sybil
continues on to evaluate the remaining
:class:`examples <sybil.Example>` in the
:class:`~sybil.Document`.

.. _integrations:

Test runner integration
-----------------------

Sybil aims to integrate with all major Python test runners. Those currently
catered for explicitly are listed below, but you may find that one of these
integration methods may work as required with other test runners.
If not, please file an issue on GitHub.

To show how the integration options work, the following documentation examples
will be tested. They use :ref:`doctests <doctest-simple-testfile>`,
:rst:dir:`code blocks <code-block>` and require a temporary directory:

.. literalinclude:: example/docs/example.rst
  :language: rest

.. _pytest_integration:

pytest
~~~~~~

To have `pytest`__ check the examples, Sybil makes use of the
``pytest_collect_file`` hook. To use this, configuration is placed in
a ``confest.py`` in your documentation source directory, as shown below.
``pytest`` should be invoked from a location that has the opportunity to
recurse into that directory:

__ https://docs.pytest.org

.. literalinclude:: example/docs/conftest.py

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

    .. literalinclude:: example/pytest.ini

.. _unitttest_integration:

unittest
~~~~~~~~

To have :ref:`unittest-test-discovery` check the example, Sybil makes use of
the `load_tests protocol`__. As such, the following should be placed in a test
module, say ``test_docs.py``, where the unit test discovery process can find it:

__ https://docs.python.org/3/library/unittest.html#load-tests-protocol

.. literalinclude:: example/example_unittest/test_example_docs.py

The ``path`` parameter gives the path, relative to the file containing this
code, that contains the documentation source files.

The file glob passed as ``pattern`` should match any documentation source
files that contain examples which you would like to be checked.

Any setup or teardown necessary for your tests can be carried out in
callables passed to the ``setup`` and ``teardown`` parameters,
which are both called with the :class:`~sybil.Document`
:class:`~sybil.Document.namespace`.

The ``fixtures`` parameter, is ignored.
