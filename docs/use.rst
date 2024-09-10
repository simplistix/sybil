Usage
=====

:term:`Sybil` works by discovering a series of :term:`documents <document>` as part of the
:term:`test runner` :doc:`integration <integration>`. These documents are then
:term:`parsed <parser>` into a set of non-overlapping
:term:`regions <region>`. When the tests are run, each :term:`region`
is turned into an :term:`example` that is :term:`evaluated <Evaluator>` in the document's
:term:`namespace`. The examples are evaluated in the order in which they appear in the
document. If an example does not evaluate as expected, a test failure is reported and :term:`Sybil`
continues on to evaluate the remaining :term:`examples <Example>` in the :term:`document`.

To use Sybil, you need pick the :ref:`integration <integrations>` for your project's test runner
and then configure appropriate :ref:`parsers <parsers>` for the examples in your project's
documentation and source code.

It's worth checking the :doc:`patterns` to see if the pattern required for your project is
covered there.

.. _integrations:

Test runner integration
-----------------------

Sybil is used by driving it through a test runner, with each example being presented as a test.
The following test runners are currently supported:

`pytest`__
  Please use the :ref:`pytest integration <pytest_integration>`.

:ref:`unittest <unittest-test-discovery>`
  Please use the :ref:`unittest integration <unitttest_integration>`.

`Twisted's trial`__
  Please use the :ref:`unittest integration <unitttest_integration>`.

__ https://docs.pytest.org

__ https://docs.twistedmatrix.com/en/stable/core/howto/trial.html

.. _parsers:

Parsers
-------

Sybil parsers are what extract examples from source files
and turns them into parsed examples with evaluators that can check if they are correct.
The parsers available depend on the source language of the files containing the examples you wish
to check:

- For ReStructured Text, typically ``.rst`` or ``.txt`` files, see :doc:`ReST Parsers <rest>`.

- For Markdown, typically ``.md`` files, :doc:`CommonMark <markdown>`,
  :doc:`GitHub Flavored Markdown <markdown>`
  and :doc:`MyST <myst>`, along with other flavours, are supported.

- For Python source code, typically ``.py`` files, it depends on the markup used in
  the docstrings; both the :doc:`ReST parsers <rest>` and :doc:`MyST parsers <myst>` will work.
  The source files are presented as :any:`PythonDocument` instances that import the document's
  source file as a Python module, making names within it available in the document's
  :attr:`~sybil.Document.namespace`.

It's also relatively easy to :doc:`develop your own parsers <parsers>`.
