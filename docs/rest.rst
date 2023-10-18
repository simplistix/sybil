Restructured Text Parsers
=========================

Sybil includes a range of parsers for extracting and checking examples from
Restructured Text including the ability to :ref:`capture <capture-parser>` previous blocks into a
variable in the :attr:`~sybil.Document.namespace`, and :ref:`skip <skip-parser>` the evaluation of
examples where necessary.

.. _doctest-parser:

doctest
-------

Parsers are included for both classic :ref:`doctest <doctest-simple-testfile>` examples
along with those in :rst:dir:`doctest` directives.
They are evaluated in the document's :attr:`~sybil.Document.namespace`.
The parsers can optionally be instantiated with
:ref:`doctest option flags<option-flags-and-directives>`.

Here are some classic :ref:`doctest <doctest-simple-testfile>` examples:

.. literalinclude:: examples/rest/doctest.rst
  :language: rest

These could be parsed with the a :class:`sybil.parsers.rest.DocTestParser` in the
following configuration:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.rest import DocTestParser
   sybil = Sybil(parsers=[DocTestParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/rest/doctest.rst', sybil, expected=3)

If you want to ensure that only examples within a :rst:dir:`doctest` directive are checked,
and any other doctest examples are ignored, then you can use the
:class:`sybil.parsers.rest.DocTestDirectiveParser` instead:

.. literalinclude:: examples/rest/doctest-directive.rst
  :language: rest

These could be checked with the following configuration:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.rest import DocTestDirectiveParser
   sybil = Sybil(parsers=[DocTestDirectiveParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/rest/doctest-directive.rst', sybil, expected=1)

.. note::

  You will have to enable :external+sphinx:doc:`sphinx.ext.doctest <usage/extensions/doctest>`
  in your ``conf.py`` for Sphinx to render :rst:dir:`doctest` directives.

.. _codeblock-parser:

Code blocks
-----------

The codeblock parsers extract examples from Sphinx :rst:dir:`code-block`
directives and evaluate them in the document's :attr:`~sybil.Document.namespace`.
The boilerplate necessary for examples to successfully evaluate and be checked
can hinder the quality of documentation.
To help with this, these parsers also evaluate "invisible" code blocks such as this one:

.. literalinclude:: examples/quickstart/example.rst
  :language: rest
  :lines: 5-9

These take advantage of Sphinx `comment`__ syntax so that the code block will
not be rendered in your documentation but can be used to set up the document's
namespace or make assertions about what the evaluation of other examples has
put in that namespace.

__ http://www.sphinx-doc.org/en/stable/rest.html#comments

Python
~~~~~~

Python code blocks can be checked using the :class:`sybil.parsers.rest.PythonCodeBlockParser`.

Here's a Python code block and an invisible Python code block that checks it:

.. literalinclude:: examples/rest/codeblock-python.rst
  :language: rest

These could be checked with the following configuration:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.rest import PythonCodeBlockParser
   sybil = Sybil(parsers=[PythonCodeBlockParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/rest/codeblock-python.rst', sybil, expected=2)

.. note::

  You should not wrap doctest examples in a ``python`` :rst:dir:`code-block`,
  they will render correctly without that and you should use the :ref:`doctest-parser`
  parser to check them.

.. _codeblock-other:

Other languages
~~~~~~~~~~~~~~~

.. note::

    If your :rst:dir:`code-block` examples define content, such as JSON or YAML, rather than
    executable code, you may find the :ref:`capture <capture-parser>` parser is more useful.

:class:`sybil.parsers.rest.CodeBlockParser` can be used to check examples in any language
you require, either by instantiating with a specified language and evaluator, or by subclassing
to create your own parser.

As an example, let's look at evaluating bash commands in a subprocess and checking the output is
as expected::

  .. code-block:: bash

     $ echo hi there
     hi there

.. -> bash_document_text

We can do this using :class:`~sybil.parsers.rest.CodeBlockParser` as follows:

.. code-block:: python

    from subprocess import check_output
    from textwrap import dedent

    from sybil import Sybil
    from sybil.parsers.codeblock import CodeBlockParser

    def evaluate_bash(example):
        command, expected = dedent(example.parsed).strip().split('\n')
        actual = check_output(command[2:].split()).strip().decode('ascii')
        assert actual == expected, repr(actual) + ' != ' + repr(expected)

    parser = CodeBlockParser(language='bash', evaluator=evaluate_bash)
    sybil = Sybil(parsers=[parser])

.. invisible-code-block: python

  from tests.helpers import check_text
  check_text(bash_document_text, sybil)

Alternatively, we can create our own parser class and use it as follows:

.. code-block:: python

    from subprocess import check_output
    from textwrap import dedent

    from sybil import Sybil
    from sybil.parsers.codeblock import CodeBlockParser

    class BashCodeBlockParser(CodeBlockParser):

        language = 'bash'

        def evaluate(self, example):
            command, expected = dedent(example.parsed).strip().split('\n')
            actual = check_output(command[2:].split()).strip().decode('ascii')
            assert actual == expected, repr(actual) + ' != ' + repr(expected)

    sybil = Sybil([BashCodeBlockParser()])

.. invisible-code-block: python

  from tests.helpers import check_text
  check_text(bash_document_text, sybil)

.. _capture-parser:

Capturing blocks
----------------

:func:`sybil.parsers.rest.CaptureParser` takes advantage of Sphinx `comment`__ syntax to introduce
a special comment that takes the preceding ReST `block`__ and inserts its
raw content into the document's :attr:`~sybil.Document.namespace`
using the name specified.

__ http://www.sphinx-doc.org/en/stable/rest.html#comments
__ http://www.sphinx-doc.org/en/stable/rest.html?highlight=block#source-code

For example::

  A simple example::

    root.txt
    subdir/
    subdir/file.txt
    subdir/logs/

  .. -> expected_listing

.. --> capture_example

This listing could be captured into the :attr:`~sybil.Document.namespace` using the following
configuration:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.rest import CaptureParser
   sybil = Sybil(parsers=[CaptureParser()])

.. invisible-code-block: python

  document = check_text(capture_example, sybil)
  expected_listing = document.namespace['expected_listing']

The above documentation source, when parsed by this parser and then evaluated,
would mean that ``expected_listing`` could be used in other examples in the
document:

>>> expected_listing.split()
['root.txt', 'subdir/', 'subdir/file.txt', 'subdir/logs/']

It can also be used with :rst:dir:`code-block` examples that define content rather
executable code, for example:

::

  .. code-block:: json

      {
          "a key": "value",
          "b key": 42
      }

  .. -> json_source

.. --> capture_example

.. invisible-code-block: python

  document = check_text(capture_example, sybil)
  json_source = document.namespace['json_source']

The JSON source can now be used as follows:

>>> import json
>>> json.loads(json_source)
{'a key': 'value', 'b key': 42}


.. note::

  It's important that the capture directive, ``.. -> json_source`` in this case, has identical
  indentation to the code block above it for this to work.

.. _skip-parser:

Skipping examples
-----------------

:class:`sybil.parsers.rest.SkipParser` takes advantage of Sphinx `comment`__ syntax to introduce
special comments that allow other examples in the document to be skipped.
This can be useful if they include pseudo code or examples that can only be
evaluated on a particular version of Python.

__ https://www.sphinx-doc.org/en/stable/rest.html#comments

For example:

.. literalinclude:: examples/rest/skip.rst
  :language: rest
  :lines: 1-6

If you need to skip a collection of examples, this can be done as follows:

.. literalinclude:: examples/rest/skip.rst
  :language: rest
  :lines: 8-15

You can also add conditions to either ``next`` or ``start`` as shown below:

.. literalinclude:: examples/rest/skip.rst
  :language: rest
  :lines: 17-24

As you can see, any names used in the expression passed to ``if`` must be
present in the document's :attr:`~sybil.Document.namespace`.
:ref:`invisible code blocks <codeblock-parser>`, :class:`setup <sybil.Sybil>`
methods or :ref:`fixtures <pytest_integration>` are good ways to provide these.

When a condition is used to skip one or more following example, it will be reported as a
skipped test in your test runner.

If you wish to have unconditional skips show up as skipped tests, this can be done as follows:


.. literalinclude:: examples/rest/skip.rst
  :language: rest
  :lines: 26-31

This can also be done when skipping collections of examples:


.. literalinclude:: examples/rest/skip.rst
  :language: rest
  :lines: 33-40


The above examples could be checked with the following configuration:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.rest import DocTestParser, SkipParser
   sybil = Sybil(parsers=[DocTestParser(), SkipParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path(
      'examples/rest/skip.rst',
      sybil,
      expected=15,
      expected_skips=('not yet working', 'Fix in v5', 'Fix in v5'),
  )

.. _clear-namespace:

Clearing the namespace
----------------------

If you want to isolate the testing of your examples within a single source file, you may want
to clear the :class:`~sybil.Document.namespace`. This can be done as follows:

.. literalinclude:: examples/rest/clear.rst
  :language: rest

The following configuration is required:

.. code-block:: python

   from sybil import Sybil
   from sybil.parsers.rest import DocTestParser, ClearNamespaceParser
   sybil = Sybil(parsers=[DocTestParser(), ClearNamespaceParser()])

.. invisible-code-block: python

  from tests.helpers import check_path
  check_path('examples/rest/clear.rst', sybil, expected=4)
