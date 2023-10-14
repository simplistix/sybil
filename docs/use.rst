Usage
=====

:class:`~sybil.Sybil` works by discovering a series of
:class:`documents <sybil.Document>` as part of the
:ref:`test runner integration <integrations>`. These documents are then
:ref:`parsed <parsers>` into a set of non-overlapping
:class:`regions <sybil.Region>`. When the tests are run, each :class:`~sybil.Region`
is turned into an :class:`~sybil.Example` that is evaluated in the document's
:class:`~sybil.Document.namespace`. The examples are evaluated
in the order in which they appear in the document.
If an example does not evaluate as expected, a test failure is reported and Sybil
continues on to evaluate the remaining
:class:`examples <sybil.Example>` in the
:class:`~sybil.Document`.

.. _integrations:

Test runner integration
-----------------------

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

.. _parsers:

Parsers
-------

Sybil parsers are what extracts examples from source files
and turns them into parsed examples with evaluators that can check if they are correct.
The parsers available depend on the source language of the files containing the examples you wish
to check:

- For ReStructured Text, typically ``.rst`` or ``.txt`` files, see :doc:`ReST Parsers <rest>`.

- For Markdown, typically ``.md`` files, :external+myst:doc:`MyST <index>` is supported.
  See :doc:`myst`.

- For Python source code, typically ``.py`` files, it depends on the markup used in
  the docstrings; both the :doc:`ReST parsers <rest>` and :doc:`MyST parsers <myst>` will work.
  The source files are presented as :any:`PythonDocument` instances that import the document's
  source file as a Python module, making names within it available in the document's
  :attr:`~sybil.Document.namespace`.

It's also relatively easy to develop your own parsers as shown in the section below.

.. _developing-parsers:

Developing your own parsers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sybil :any:`parsers <Parser>` are callables that take a
:class:`~sybil.Document` and yield a sequence of regions. A :class:`~sybil.Region` contains
the character position of the :attr:`~sybil.Region.start` and :attr:`~sybil.Region.end`
of the example in the document's
:attr:`~sybil.Document.text`, along with a :attr:`~sybil.Region.parsed` version of the
example and a callable :attr:`~sybil.Region.evaluator`.
Parsers are free to access any documented attribute of the :class:`~sybil.Document` although
will most likely only need to work with :attr:`~sybil.Document.text`.
The :attr:`~sybil.Document.namespace` attribute should **not** be modified.

The :attr:`~sybil.Region.parsed` version can take any form and only needs to be understood by the
:attr:`~sybil.Region.evaluator`.

That evaluator will be called with an
:class:`~sybil.Example` constructed from the
:class:`~sybil.Document` and the :class:`~sybil.Region`
and should return a :ref:`false value <truth>` if the example is as expected. Otherwise, it should
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
:any:`lexers <Lexer>` already exist for the source language containing your examples.

Failing that, parsers quite often use regular expressions to extract the text for examples
from the document. There's no hard requirement for this, but if you find you need to, then
:meth:`~sybil.Document.find_region_sources` may be of help.

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

Finally, the parser could be implemented from scratch, with the parsed version again consisting of
a tuple of the command to run and the expected output:

.. code-block:: python

    from subprocess import check_output
    import re, textwrap
    from sybil import Sybil, Region

    BASHBLOCK_START = re.compile(r'^\.\.\s*code-block::\s*bash')
    BASHBLOCK_END = re.compile(r'(\n\Z|\n(?=\S))')

    def evaluate_bash_block(example):
        command, expected = example.parsed
        actual = check_output(command).strip().decode('ascii')
        assert actual == expected, repr(actual) + ' != ' + repr(expected)

    def parse_bash_blocks(document):
        for start_match, end_match, source in document.find_region_sources(
            BASHBLOCK_START, BASHBLOCK_END
        ):
            command, output = textwrap.dedent(source).strip().split('\n')
            assert command.startswith('$ ')
            parsed = command[2:].split(), output
            yield Region(start_match.start(), end_match.end(),
                         parsed, evaluate_bash_block)

    sybil = Sybil(parsers=[parse_bash_blocks], pattern='*.rst')

.. invisible-code-block: python

  from tests.helpers import check_text
  check_text(bash_document_text, sybil)
