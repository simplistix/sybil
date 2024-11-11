Developing your own parsers
===========================

Sybil :term:`parsers <Parser>` are callables that take a
:term:`document` and yield a sequence of :term:`regions <region>`. A :term:`region` contains
the character position of the :attr:`~sybil.Region.start` and :attr:`~sybil.Region.end`
of the example in the document's
:attr:`~sybil.Document.text`, along with a :attr:`~sybil.Region.parsed` version of the
example and a callable :attr:`~sybil.Region.evaluator`.
Parsers are free to access any documented attribute of the :class:`~sybil.Document` although
will most likely only need to work with :attr:`~sybil.Document.text`.
The :attr:`~sybil.Document.namespace` attribute should **not** be modified.

The :attr:`~sybil.Region.parsed` version can take any form and only needs to be understood by the
:attr:`~sybil.Region.evaluator`.

That :term:`evaluator` will be called with an :term:`example` constructed from the
:term:`document` and the :term:`region` and should return a :ref:`false value <truth>`
if the example is as expected. Otherwise, it should
either raise an exception or return a textual description in the
event of the example not being as expected. Evaluators may also
modify the document's :attr:`~sybil.Document.namespace`
or :any:`push <sybil.Document.push_evaluator>` and
:any:`pop <sybil.Document.pop_evaluator>` evaluators.

:class:`~sybil.Example` instances are used to wrap up
all the attributes you're likely to need when writing an evaluator and all
documented attributes are fine to use. In particular,
:attr:`~sybil.Example.parsed` is the parsed value provided by the parser
when instantiating the :class:`~sybil.Region` and
:attr:`~sybil.Example.namespace` is a reference to the document's
namespace. Evaluators **are** free to modify the
:attr:`~sybil.Document.namespace` if they need to.

If you need to write your own parser, you should consult the :doc:`api` so see if suitable
:term:`lexers <Lexer>` already exist for the source language containing your examples.

Worked example
~~~~~~~~~~~~~~

As an example, let's look at a parser suitable for evaluating bash commands
in a subprocess and checking the output is as expected::

  .. code-block:: bash

     $ echo hi there
     hi there

.. -> bash_document_text

Since this is a ReStructured Text code block, the simplest thing we could do would be to use
the existing support for :ref:`other languages <codeblock-other>`:

.. code-block:: python

    from subprocess import check_output
    from sybil import Sybil
    from sybil.parsers.rest import CodeBlockParser

    def evaluate_bash_block(example):
        command, expected = example.parsed.strip().split('\n')
        assert command.startswith('$ ')
        command = command[2:].split()
        actual = check_output(command).strip().decode('ascii')
        assert actual == expected, repr(actual) + ' != ' + repr(expected)

    parser = CodeBlockParser(language='bash', evaluator=evaluate_bash_block)

    sybil = Sybil(parsers=[parser], pattern='*.rst')


.. invisible-code-block: python

  from tests.helpers import check_text
  check_text(bash_document_text, sybil)

Another alternative would be to start with the
:class:`lexer for ReST directives <sybil.parsers.rest.lexers.DirectiveLexer>`.
Here, the parsed version consists of a tuple of the command to run and the expected output:

.. code-block:: python

    from subprocess import check_output
    from typing import Iterable
    from sybil import Sybil, Document, Region, Example
    from sybil.parsers.rest.lexers import DirectiveLexer

    from subprocess import check_output

    def evaluate_bash_block(example: Example):
        command, expected = example.parsed
        actual = check_output(command).strip().decode('ascii')
        assert actual == expected, repr(actual) + ' != ' + repr(expected)

    def parse_bash_blocks(document: Document) -> Iterable[Region]:
        lexer = DirectiveLexer(directive='code-block', arguments='bash')
        for lexed in lexer(document):
            command, output = lexed.lexemes['source'].strip().split('\n')
            assert command.startswith('$ ')
            parsed = command[2:].split(), output
            yield Region(lexed.start, lexed.end, parsed, evaluate_bash_block)

    sybil = Sybil(parsers=[parse_bash_blocks], pattern='*.rst')

.. invisible-code-block: python

  from tests.helpers import check_text
  check_text(bash_document_text, sybil)

.. _parser-from-scratch:

Finally, the parser could be implemented from scratch, with the parsed version again consisting of
a tuple of the command to run and the expected output:

.. code-block:: python

    from subprocess import check_output
    import re, textwrap
    from sybil import Sybil, Region
    from sybil.parsers.abstract.lexers import BlockLexer

    BASHBLOCK_START = re.compile(r'^\.\.\s*code-block::\s*bash')
    BASHBLOCK_END = r'(\n\Z|\n(?=\S))'

    def evaluate_bash_block(example):
        command, expected = example.parsed
        actual = check_output(command).strip().decode('ascii')
        assert actual == expected, repr(actual) + ' != ' + repr(expected)

    def parse_bash_blocks(document):
        lexer = BlockLexer(BASHBLOCK_START, BASHBLOCK_END)
        for region in lexer(document):
            command, output = region.lexemes['source'].strip().split('\n')
            assert command.startswith('$ ')
            region.parsed = command[2:].split(), output
            region.evaluator = evaluate_bash_block
            yield region

    sybil = Sybil(parsers=[parse_bash_blocks], pattern='*.rst')

.. invisible-code-block: python

  from tests.helpers import check_text
  check_text(bash_document_text, sybil)
