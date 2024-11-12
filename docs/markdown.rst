Markdown Parsers
================

Sybil supports `Markdown`__, including `GitHub Flavored Markdown`__ and
:external+myst:doc:`MyST <index>`.
If you are using MyST, then you should use the :doc:`MyST parsers <myst>`.
For other flavors of markdown, the parsers described below support extracting and checking
examples from Markdown source, including the ability to :ref:`skip <markdown-skip-parser>` the
evaluation of examples where necessary.

__ https://commonmark.org/

__ https://github.github.com/markdown/


.. _markdown-doctest-parser:

doctest
-------

Doctest examples in ``python`` `fenced code blocks`__, can be checked with
the :class:`~sybil.parsers.markdown.PythonCodeBlockParser`.

__ https://spec.commonmark.org/0.30/#fenced-code-blocks

For example:

.. literalinclude:: examples/markdown/doctest.md
  :language: markdown


Both examples in the single block above can be checked with the following
configuration:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.markdown import PythonCodeBlockParser
   sybil = Sybil(parsers=[PythonCodeBlockParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/markdown/doctest.md', sybil, expected=2)

.. _markdown-codeblock-parser:

Code blocks
-----------

The codeblock parsers extract examples from `fenced code blocks`__ and "invisible"
code blocks in HTML-style Markdown mult-line comments.

__ https://spec.commonmark.org/0.30/#fenced-code-blocks

Python
~~~~~~

Python examples can be checked in ``python`` `fenced code blocks`__  using the
:class:`~sybil.parsers.markdown.PythonCodeBlockParser`.

__ https://spec.commonmark.org/0.30/#fenced-code-blocks

Including all the boilerplate necessary for examples to successfully evaluate and be checked
can hinder writing documentation. To help with this, "invisible" code blocks are also supported.
These take advantage of HTML-style Markdown block comments.

For example:

.. literalinclude:: examples/markdown/codeblock-python.md
  :language: markdown

These examples can be checked with the following configuration:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.markdown import PythonCodeBlockParser
   sybil = Sybil(parsers=[PythonCodeBlockParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/markdown/codeblock-python.md', sybil, expected=1)


.. _markdown-codeblock-other:

Other languages
~~~~~~~~~~~~~~~

:class:`~sybil.parsers.markdown.CodeBlockParser` can be used to check examples in any language
you require, either by instantiating with a specified language and evaluator, or by subclassing
to create your own parser.

As an example, let's look at evaluating bash commands in a subprocess and checking the output is
as expected:

.. literalinclude:: examples/markdown/codeblock-bash.md
  :language: markdown

.. -> bash_document_text

We can do this using :class:`~sybil.parsers.markdown.CodeBlockParser` as follows:

.. code-block:: python

    from subprocess import check_output
    from textwrap import dedent

    from sybil import Sybil
    from sybil.parsers.markdown import CodeBlockParser

    def evaluate_bash(example):
        command, expected = dedent(example.parsed).strip().split('\n')
        actual = check_output(command[2:].split()).strip().decode('ascii')
        assert actual == expected, repr(actual) + ' != ' + repr(expected)

    parser = CodeBlockParser(language='bash', evaluator=evaluate_bash)
    sybil = Sybil(parsers=[parser])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/markdown/codeblock-bash.md', sybil, expected=1)

Alternatively, we can create our own parser class and use it as follows:

.. code-block:: python

    from subprocess import check_output
    from textwrap import dedent

    from sybil import Sybil
    from sybil.parsers.markdown import CodeBlockParser

    class BashCodeBlockParser(CodeBlockParser):

        language = 'bash'

        def evaluate(self, example):
            command, expected = dedent(example.parsed).strip().split('\n')
            actual = check_output(command[2:].split()).strip().decode('ascii')
            assert actual == expected, repr(actual) + ' != ' + repr(expected)

    sybil = Sybil([BashCodeBlockParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/markdown/codeblock-bash.md', sybil, expected=1)

.. _markdown-skip-parser:

Skipping examples
-----------------

:class:`~sybil.parsers.markdown.SkipParser` takes advantage of Markdown comments to allow checking of
specified examples to be skipped.

For example:

.. literalinclude:: examples/markdown/skip.md
  :language: markdown
  :lines: 1-8

If you need to skip a collection of examples, this can be done as follows:

.. literalinclude:: examples/markdown/skip.md
  :language: markdown
  :lines: 10-25

You can also add conditions to either ``next`` or ``start`` as shown below:

.. literalinclude:: examples/markdown/skip.md
  :language: markdown
  :lines: 27-38

As you can see, any names used in the expression passed to ``if`` must be
present in the document's :attr:`~sybil.Document.namespace`.
:ref:`invisible code blocks <markdown-codeblock-parser>`, :class:`setup <sybil.Sybil>`
methods or :ref:`fixtures <pytest_integration>` are good ways to provide these.

When a condition is used to skip one or more following example, it will be reported as a
skipped test in your test runner.

If you wish to have unconditional skips show up as skipped tests, this can be done as follows:


.. literalinclude:: examples/markdown/skip.md
  :language: markdown
  :lines: 40-47

This can also be done when skipping collections of examples:


.. literalinclude:: examples/markdown/skip.md
  :language: markdown
  :lines: 49-58

The above examples could be checked with the following configuration:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.markdown import PythonCodeBlockParser, SkipParser
   sybil = Sybil(parsers=[PythonCodeBlockParser(), SkipParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path(
      'examples/markdown/skip.md',
      sybil,
      expected=15,
      expected_skips=('not yet working', 'Fix in v5', 'Fix in v5'),
  )

.. _markdown-clear-namespace:

Clearing the namespace
----------------------

If you want to isolate the testing of your examples within a single source file, you may want
to clear the :class:`~sybil.Document.namespace`. This can be done as follows:

.. literalinclude:: examples/markdown/clear.md
  :language: rest

The following configuration is required:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.markdown import PythonCodeBlockParser, ClearNamespaceParser
   sybil = Sybil(parsers=[PythonCodeBlockParser(), ClearNamespaceParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/markdown/clear.md', sybil, expected=4)
