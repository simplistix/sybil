MyST Parsers
============

Sybil includes a range of parsers for extracting and checking examples from
:external+myst:doc:`MyST <index>` including the ability to :ref:`skip <myst-skip-parser>` the
evaluation of examples where necessary.

.. _myst-doctest-parser:

doctest
-------

A selection of parsers are included that can extract and check doctest examples in
``python`` `fenced code blocks`__,
MyST ``code-block`` :ref:`directives <syntax/directives>` and
MyST ``doctest`` :ref:`directives <syntax/directives>`.

__ https://spec.commonmark.org/0.30/#fenced-code-blocks

Most cases can be covered using a :class:`sybil.parsers.myst.PythonCodeBlockParser`.
For example:

.. literalinclude:: examples/myst/doctest.md
  :language: markdown


All three examples in the two blocks above can be checked with the following
configuration:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.myst import PythonCodeBlockParser
   sybil = Sybil(parsers=[PythonCodeBlockParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/myst/doctest.md', sybil, expected=3)

Alternatively, the ReST :ref:`doctest parser <doctest-parser>` will
find all doctest examples in a Markdown file. If any should not be checked,
you can make use of the :ref:`skip <myst-skip-parser>` parser.

.. note::

  You can only use the ReST :ref:`doctest parser <doctest-parser>` if no doctest
  examples are contained in examples parsed by the other parsers listed here.
  If you do, :class:`ValueError` exceptions relating to overlapping regions will be raised.

``doctest`` directive
~~~~~~~~~~~~~~~~~~~~~

If you have made use of MyST ``doctest`` :ref:`directives <syntax/directives>`
such as this:

.. literalinclude:: examples/myst/doctest-directive.md
  :language: markdown

You can use the :class:`sybil.parsers.myst.DocTestDirectiveParser` as follows:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.myst import DocTestDirectiveParser
   sybil = Sybil(parsers=[DocTestDirectiveParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/myst/doctest-directive.md', sybil, expected=2)

.. note::

  You will have to enable :external+sphinx:doc:`sphinx.ext.doctest <usage/extensions/doctest>`
  in your ``conf.py`` for Sphinx to render :rst:dir:`doctest` directives.

``eval-rst`` directive
~~~~~~~~~~~~~~~~~~~~~~

If you have used ReST :rst:dir:`doctest` directive inside a MyST ``eval-rst``
:ref:`directive <syntax/directives>` such as this:


.. literalinclude:: examples/myst/doctest-eval-rst.md
  :language: markdown


Then you would use the normal :class:`sybil.parsers.rest.DocTestDirectiveParser` as follows:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.rest import DocTestDirectiveParser as ReSTDocTestDirectiveParser
   sybil = Sybil(parsers=[ReSTDocTestDirectiveParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/myst/doctest-eval-rst.md', sybil, expected=1)

.. note::

  You will have to enable :external+sphinx:doc:`sphinx.ext.doctest <usage/extensions/doctest>`
  in your ``conf.py`` for Sphinx to render :rst:dir:`doctest` directives.

.. _myst-codeblock-parser:

Code blocks
-----------

The codeblock parsers extract examples from `fenced code blocks`__,
MyST ``code-block`` :ref:`directives <syntax/directives>` and "invisible"
code blocks in both styles of Markdown mult-line comment.

__ https://spec.commonmark.org/0.30/#fenced-code-blocks

Python
~~~~~~

Python examples can be checked in either ``python`` `fenced code blocks`__ or
MyST ``code-block`` :ref:`directives <syntax/directives>` using the
:class:`sybil.parsers.myst.PythonCodeBlockParser`.

__ https://spec.commonmark.org/0.30/#fenced-code-blocks

Including all the boilerplate necessary for examples to successfully evaluate and be checked
can hinder writing documentation. To help with this, "invisible" code blocks are also supported.
These take advantage of either style of Markdown block comments.

For example:

.. literalinclude:: examples/myst/codeblock-python.md
  :language: markdown

These examples can be checked with the following configuration:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.myst import PythonCodeBlockParser
   sybil = Sybil(parsers=[PythonCodeBlockParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/myst/codeblock-python.md', sybil, expected=4)


.. _myst-codeblock-other:

Other languages
~~~~~~~~~~~~~~~

:class:`sybil.parsers.myst.CodeBlockParser` can be used to check examples in any language
you require, either by instantiating with a specified language and evaluator, or by subclassing
to create your own parser.

As an example, let's look at evaluating bash commands in a subprocess and checking the output is
as expected:

.. literalinclude:: examples/myst/codeblock-bash.md
  :language: markdown

.. -> bash_document_text

We can do this using :class:`~sybil.parsers.myst.CodeBlockParser` as follows:

.. code-block:: python

    from subprocess import check_output
    from textwrap import dedent

    from sybil import Sybil
    from sybil.parsers.myst import CodeBlockParser

    def evaluate_bash(example):
        command, expected = dedent(example.parsed).strip().split('\n')
        actual = check_output(command[2:].split()).strip().decode('ascii')
        assert actual == expected, repr(actual) + ' != ' + repr(expected)

    parser = CodeBlockParser(language='bash', evaluator=evaluate_bash)
    sybil = Sybil(parsers=[parser])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/myst/codeblock-bash.md', sybil, expected=1)

Alternatively, we can create our own parser class and use it as follows:

.. code-block:: python

    from subprocess import check_output
    from textwrap import dedent

    from sybil import Sybil
    from sybil.parsers.myst import CodeBlockParser

    class BashCodeBlockParser(CodeBlockParser):

        language = 'bash'

        def evaluate(self, example):
            command, expected = dedent(example.parsed).strip().split('\n')
            actual = check_output(command[2:].split()).strip().decode('ascii')
            assert actual == expected, repr(actual) + ' != ' + repr(expected)

    sybil = Sybil([BashCodeBlockParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/myst/codeblock-bash.md', sybil, expected=1)

.. _myst-skip-parser:

Skipping examples
-----------------

:class:`sybil.parsers.myst.SkipParser` takes advantage of Markdown comments to allow checking of
specified examples to be skipped.

For example:

.. literalinclude:: examples/myst/skip.md
  :language: markdown
  :lines: 1-8

You can also use HTML-style comments:


.. literalinclude:: examples/myst/skip.md
  :language: markdown
  :lines: 60-67


If you need to skip a collection of examples, this can be done as follows:

.. literalinclude:: examples/myst/skip.md
  :language: markdown
  :lines: 10-25

You can also add conditions to either ``next`` or ``start`` as shown below:

.. literalinclude:: examples/myst/skip.md
  :language: markdown
  :lines: 27-38

As you can see, any names used in the expression passed to ``if`` must be
present in the document's :attr:`~sybil.Document.namespace`.
:ref:`invisible code blocks <myst-codeblock-parser>`, :class:`setup <sybil.Sybil>`
methods or :ref:`fixtures <pytest_integration>` are good ways to provide these.

When a condition is used to skip one or more following example, it will be reported as a
skipped test in your test runner.

If you wish to have unconditional skips show up as skipped tests, this can be done as follows:


.. literalinclude:: examples/myst/skip.md
  :language: markdown
  :lines: 40-47

This can also be done when skipping collections of examples:


.. literalinclude:: examples/myst/skip.md
  :language: markdown
  :lines: 49-58

The above examples could be checked with the following configuration:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.myst import PythonCodeBlockParser, SkipParser
   sybil = Sybil(parsers=[PythonCodeBlockParser(), SkipParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path(
      'examples/myst/skip.md',
      sybil,
      expected=17,
      expected_skips=('not yet working', 'Fix in v5', 'Fix in v5'),
  )

.. _myst-clear-namespace:

Clearing the namespace
----------------------

If you want to isolate the testing of your examples within a single source file, you may want
to clear the :class:`~sybil.Document.namespace`. This can be done as follows:

.. literalinclude:: examples/myst/clear.md
  :language: rest

The following configuration is required:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.myst import PythonCodeBlockParser, ClearNamespaceParser
   sybil = Sybil(parsers=[PythonCodeBlockParser(), ClearNamespaceParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/myst/clear.md', sybil, expected=4)

You can also used HTML-style comments as follows:

.. literalinclude:: examples/myst/clear-html-comment.md
  :language: rest

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/myst/clear-html-comment.md', sybil, expected=4)
