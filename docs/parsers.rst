Parsers
=======

Sybil parsers are what extracts examples from source files
and turns them into parsed examples with evaluators that can check if they
are as expected. A number of parsers are included, and it's simple enough to
write your own. The included parsers are as follows:

.. _doctest-parser:

doctest
-------

This parser extracts classic :ref:`doctest <doctest-simple-testfile>` examples
and evaluates them in the document's :attr:`~sybil.Document.namespace`.
The parser can optionally be instantiated with
:ref:`doctest option flags<option-flags-and-directives>`.

An additional option flag, :attr:`sybil.parsers.doctest.FIX_BYTE_UNICODE_REPR`, is provided.
When used, this flag causes byte and unicode literals in doctest expected
output to be rewritten such that they are compatible with the version of
Python with which the tests are executed. If your example output includes either
``b'...'`` or ``u'...'`` and your code is expected to run under both Python 2
and Python 3, then you will likely need this option.

The parser is used by instantiating :class:`sybil.parsers.doctest.DocTestParser`
with the required options and passing it as an element in the list passed as the
``parsers`` parameter to :class:`~sybil.Sybil`.

.. warning::

    :attr:`~sybil.parsers.doctest.FIX_BYTE_UNICODE_REPR` is quite simplistic. It will catch
    examples but you may hit problems where, for example, ``['b', '']`` in expected
    output will be rewritten as ``['', '']`` on Python 2 and ``['u', '']`` as ``['', '']``.
    on Python 3. To work around this, either only run Sybil on Python 3 and do not
    use this option, or pick different example output.

.. _codeblock-parser:

codeblock
---------

The parsers in :mod:`sybil.parsers.codeblock` extract examples from Sphinx :rst:dir:`code-block`
directives and evaluate them in the document's :attr:`~sybil.Document.namespace`.

Including all the boilerplate necessary for examples to successfully evaluate and be checked
can hinder writing documentation. To help with this, these parsers also evaluate "invisible" code
blocks such as this one:

.. literalinclude:: example.rst
  :language: rest
  :lines: 5-9

These take advantage of Sphinx `comment`__ syntax so that the code block will
not be rendered in your documentation but can be used to set up the document's
namespace or make assertions about what the evaluation of other examples has
put in that namespace.

__ http://www.sphinx-doc.org/en/stable/rest.html#comments

Python
~~~~~~

Python code blocks can be checked by instantiating
:class:`sybil.parsers.codeblock.PythonCodeBlockParser` and passing it as an element in
the list passed as the ``parsers`` parameter to :class:`~sybil.Sybil`.

For example, this Python code block would be evaluated successfully and will define the
:func:`prefix_and_print` function in the document's namespace:

.. literalinclude:: example.rst
  :language: rest
  :lines: 11-18

:class:`~sybil.parsers.codeblock.PythonCodeBlockParser` takes an optional
``future_imports`` parameter that can be used to prefix all example python
code found by this parser with one or or more ``from __future__ import ...``
statements. For example, to prefix all code block examples with
``from __future__ import print_function``, such that they can use Python 3 style
``print()`` calls even when testing the documentation under Python 2, you would
instantiate the parser as follows:

.. code-block:: python

  from sybil.parsers.codeblock import PythonCodeBlockParser

  PythonCodeBlockParser(future_imports=['print_function'])

.. _codeblock-other:

Other Languages
~~~~~~~~~~~~~~~

.. note::

    If your :rst:dir:`code-block` examples define content rather executable code, you may
    find the :ref:`capture <capture-parser>` parser is more useful.

:class:`sybil.parsers.codeblock.CodeBlockParser` can be used to check examples in any language
you require, either by instantiating with a specified language and evaluator, or by subclassing
to create your own parser.

As an example, let's look at evaluating bash commands in a subprocess and checking the output is
as expected::

  .. code-block:: bash

     $ echo hi there
     hi there

.. -> bash_document_text

We can do this using :class:`~sybil.parsers.codeblock.CodeBlockParser` as follows:

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
    sybil = Sybil(parsers=[parser], pattern='*.rst')

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

    sybil = Sybil([BashCodeBlockParser()], pattern='*.rst')

.. invisible-code-block: python

  from tests.helpers import check_text
  check_text(bash_document_text, sybil)

.. _capture-parser:

capture
-------

This parser takes advantage of Sphinx `comment`__ syntax to introduce
a special comment that takes the preceding ReST `block`__ and inserts its
raw content into the document's :attr:`~sybil.Document.namespace`
using the name specified.

__ http://www.sphinx-doc.org/en/stable/rest.html#comments
__ http://www.sphinx-doc.org/en/stable/rest.html?highlight=block#source-code

It is used by including :func:`sybil.parsers.capture.parse_captures`
as an element in the list passed as the
``parsers`` parameter to :class:`~sybil.Sybil`.

For example::

  A simple example::

    root.txt
    subdir/
    subdir/file.txt
    subdir/logs/

  .. -> expected_listing

.. --> capture_example

.. invisible-code-block: python

  from sybil.parsers.capture import parse_captures
  sybil =  Sybil([parse_captures], pattern='*.rst')
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

skip
----

This parser takes advantage of Sphinx `comment`__ syntax to introduce
special comments that allow other examples in the document to be skipped.
This can be useful if they include pseudo code or examples that can only be
evaluated on a particular version of Python.

__ http://www.sphinx-doc.org/en/stable/rest.html#comments

For example:

.. literalinclude:: example-skip.rst
  :language: rest
  :lines: 1-6

If you need to skip a collection of examples, this can be done as follows:

.. literalinclude:: example-skip.rst
  :language: rest
  :lines: 8-15

You can also add conditions to either ``next`` or ``start`` as shown below:

.. literalinclude:: example-skip.rst
  :language: rest
  :lines: 17-

As you can see, any names used in the expression passed to ``if`` must be
present in the document's :attr:`~sybil.Document.namespace`.
:ref:`invisible code blocks <codeblock-parser>`, :class:`setup <sybil.Sybil>`
methods or :ref:`fixtures <pytest_integration>` are good ways to provide these.

The parser is used by including :func:`sybil.parsers.skip.skip`
as an element in the list passed as the
``parsers`` parameter to :class:`~sybil.Sybil`.

.. _developing-parsers:

Developing your own parsers
---------------------------

Sybil parsers are callables that take a
:class:`sybil.Document` and yield a sequence of
:class:`regions <sybil.Region>`. A :class:`~sybil.Region` contains
the character position of the start and end of the example in the document's
:attr:`~sybil.Document.text`, along with a parsed version of the
example and a callable evaluator. That evaluator will be called with an
:class:`~sybil.Example` constructed from the
:class:`~sybil.Document` and the :class:`~sybil.Region`
and should either raise an exception or return a textual description in the
event of the example not being as expected. Evaluators may also
modify the document's :attr:`~sybil.Document.namespace`
or :attr:`~sybil.Document.evaluator`.

As an example, let's look at a parser suitable for evaluating bash commands
in a subprocess and checking the output is as expected::

  .. code-block:: bash

     $ echo hi there
     hi there

.. -> bash_document_text

.. note::

  This specific case can more easily be dealt with using the :rst:dir:`code-block`
  support for :ref:`other languages<codeblock-other>`.

Writing parsers quite often involves using regular expressions to extract
the text for examples from the document. There's no hard requirement
for this, but if you find you need to, then
:meth:`~sybil.Document.find_region_sources` may be of help.
Parsers are free to access any documented attribute of the
:class:`~sybil.Document` although will most likely
only need to work with :attr:`~sybil.Document.text`.
The :attr:`~sybil.Document.namespace` attribute should **not** be
modified.

For the above example, the parser could be implemented as follows, with the
parsed version consisting of a tuple of the command to run and the expected
output:

.. code-block:: python

    import re, textwrap
    from sybil import Region

    BASHBLOCK_START = re.compile(r'^\.\.\s*code-block::\s*bash')
    BASHBLOCK_END = re.compile(r'(\n\Z|\n(?=\S))')

    def parse_bash_blocks(document):
        for start_match, end_match, source in document.find_region_sources(
            BASHBLOCK_START, BASHBLOCK_END
        ):
            command, output = textwrap.dedent(source).strip().split('\n')
            assert command.startswith('$ ')
            parsed = command[2:].split(), output
            yield Region(start_match.start(), end_match.end(),
                         parsed, evaluate_bash_block)

Evaluators are generally much simpler than parsers and are called with an
:class:`~sybil.Example`. Instances of this class are used to wrap up
all the attributes you're likely to need when writing an evaluator and all
documented attributes are fine to use. In particular,
:attr:`~sybil.Example.parsed` is the parsed value provided by the parser
when instantiating the :class:`~sybil.Region` and
:attr:`~sybil.Example.namespace` is a reference to the document's
namespace. Evaluators **are** free to modify the
:attr:`~sybil.Document.namespace` if they need to.

For the above example, the evaluator could be implemented as follows:

.. code-block:: python

    from subprocess import check_output

    def evaluate_bash_block(example):
        command, expected = example.parsed
        actual = check_output(command).strip().decode('ascii')
        assert actual == expected, repr(actual) + ' != ' + repr(expected)

The parser can now be used when instantiating a :class:`~sybil.Sybil`, which can
then be used to integrate with your test runner:

.. code-block:: python

    from sybil import Sybil

    sybil = Sybil(parsers=[parse_bash_blocks], pattern='*.rst')

.. invisible-code-block: python

  check_text(bash_document_text, sybil)
