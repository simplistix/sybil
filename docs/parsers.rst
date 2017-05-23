Parsers
=======

Sybil parsers are what extracts examples from documentation source files
and turns them into parsed examples with evaluators that can check if they
are as expected. A number of parsers are included, and it's simple enough to
write your own. The included parsers are as follows:

doctest
-------

This parser extracts classic :ref:`doctest <doctest-simple-testfile>` examples
and evaluates them in the document's :attr:`~sybil.document.Document.namespace`.
The parser can optionally be instantiated with
:ref:`doctest option flags<option-flags-and-directives>`.

An additional option flag, :attr:`sybil.parsers.doctest.FIX_BYTE_UNICODE_REPR`, is provided.
When used, this flag causes byte and unicode literals in doctest expected
output to be rewritten such that they are compatible with the version of
Python with with the tests are executed. If your example output includes either
``b'...'`` or ``u'...'`` and your code is expected to run under both Python 2
and Python 3, then you will likely need this option.

The parser is used by instantiating :class:`sybil.parsers.doctest.DocTestParser`
with the required options and passing it as an element in the list passed as the
``parsers`` parameter to :class:`~sybil.Sybil`.

codeblock
---------

This parser extracts examples from Sphinx :rst:dir:`code-block` directives
and evaluates them in the document's :attr:`~sybil.document.Document.namespace`.

For example, this code block would be evaluated successfully and will define the
:func:`prefix_and_print` function in the document's namespace:

.. literalinclude:: example.rst
  :language: rest
  :lines: 11-18

Including all the boilerplate necessary for an example to successfully evaluate
can hinder an example's usefulness as part of documentation. As a result, this
parser also evaluates "invisible" code blocks such as this one:

.. literalinclude:: example.rst
  :language: rest
  :lines: 5-9

These take advantage of Sphinx `comment`__ syntax so that the code block will
not be rendered in your documentation but can be used to set up the document's
namespace or make assertions about what the evaluation of other examples has
put in that namespace.

__ http://www.sphinx-doc.org/en/stable/rest.html#comments

The parser is used by instantiating
:class:`sybil.parsers.codeblock.CodeBlockParser` and passing it as an element in
the list passed as the ``parsers`` parameter to :class:`~sybil.Sybil`.
:class:`~sybil.parsers.codeblock.CodeBlockParser` takes an optional
``future_imports`` parameter that can be used to prefix all example python
code found by this parser with one or or more ``from __future__ import ...``
statements. For example, to prefix all code block examples with
``from __future__ import print_function``, such that they can use Python 3 style
``print()`` calls even when testing the documentation under Python 2, you would
instantiate the parser as follows:

.. code-block:: python

  from sybil.parsers.codeblock import CodeBlockParser

  CodeBlockParser(future_imports=['print_function'])

capture
-------

This parser takes advantage of Sphinx `comment`__ syntax to introduce
a special comment that takes the preceding ReST `block`__ and inserts its
raw content into the document's :attr:`~sybil.document.Document.namespace`
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

.. invisible-code-block: python

  from sybil.document import Document
  from sybil.parsers.capture import parse_captures
  document = Document(capture_example, '/the/path')
  (region,) = parse_captures(document)
  document.add(region)
  (example,) = document
  region.evaluator(example)
  expected_listing = document.namespace['expected_listing']

The above documentation source, when parsed by this parser and then evaluated,
would mean that ``expected_listing`` could be used in other examples in the
document:

>>> expected_listing.split()
['root.txt', 'subdir/', 'subdir/file.txt', 'subdir/logs/']

The parser is used by including :func:`sybil.parsers.capture.parse_captures`
as an element in the list passed as the
``parsers`` parameter to :class:`~sybil.Sybil`.
