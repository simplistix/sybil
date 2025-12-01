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

    bash_parser = CodeBlockParser(language='bash', evaluator=evaluate_bash_block)

    sybil = Sybil(parsers=[bash_parser], pattern='*.rst')


.. invisible-code-block: python

  from sybil.testing import check_sybil
  check_sybil(sybil, bash_document_text)

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

  from sybil.testing import check_sybil
  check_sybil(sybil, bash_document_text)

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

  from sybil.testing import check_sybil
  check_sybil(sybil, bash_document_text)

Of course, you should also write tests for your parser, showing it both succeeding and failing.
Here are examples for the Bash parser implementation at the start of this section, making use
of :func:`~sybil.testing.check_parser` to check a single example in a string against the supplied
:data:`~sybil.typing.Parser`:

.. code-block:: python

    from sybil.testing import check_parser
    from testfixtures import ShouldAssert

    def test_bash_success() -> None:
        check_parser(
            bash_parser,
            text="""
                .. code-block:: bash

                    $ echo hi there
                    hi there
            """,
        )

    def test_bash_failure() -> None:
        with ShouldAssert("'this is wrong' != 'hi there'"):
            check_parser(
                bash_parser,
                text="""
                    .. code-block:: bash

                        $ echo this is wrong
                        hi there
                """,
            )

.. invisible-code-block: python

  test_bash_success()
  test_bash_failure()

Developing with Lexers
~~~~~~~~~~~~~~~~~~~~~~

Sybil has a fairly rich selection of :term:`parsers <Parser>` and :term:`lexers <Lexer>` such that
even if your source format isn't directly supported, you may not have too much work to do in order
to support it.

Take `Docusaurus code blocks`__, which add parameters to Markdown fenced code blocks. Suppose we
want to implement a parser which will execute Python code blocks in this format:

.. code-block:: markdown

    ```python title="hello.py"
    print("hello")
    ```

__ https://docusaurus.io/docs/markdown-features/code-blocks

Firstly, let's implement a lexer that understands this extension to the markdown format:

.. code-block:: python

    from sybil.parsers.markdown.lexers import RawFencedCodeBlockLexer

    class DocusaurusCodeBlockLexer(RawFencedCodeBlockLexer):

        def __init__(self) -> None:
            super().__init__(
                info_pattern=re.compile(
                    r'^(?P<language>\w+)(?:\s+(?P<params>.+))?$\n', re.MULTILINE
                ),
            )

        def __call__(self, document: Document) -> Iterable[Region]:
            for lexed in super().__call__(document):
                lexemes = lexed.lexemes
                raw_params = lexemes.pop('params', None)
                params = lexemes['params'] = {}
                if raw_params:
                    for match in re.finditer(r'(?P<key>\w+)="(?P<value>[^"]*)"', raw_params):
                        params[match.group('key')] = match.group('value')
                yield lexed

We can write a unit test that verifies this lexer works as follows:

.. code-block:: python

    from sybil import Region
    from sybil.testing import check_lexer

    def test_docusaurus_lexing() -> None:
        regions = check_lexer(
            lexer=DocusaurusCodeBlockLexer(),
            source_text="""
                ```jsx title="/src/components/HelloCodeTitle.js"
                function HelloCodeTitle(props) {
                  return <h1>Hello, {props.name}</h1>;
                }
                ```
            """,
            expected_text=(
                '            ```jsx title="/src/components/HelloCodeTitle.js"\n'
                '            function HelloCodeTitle(props) {\n'
                '              return <h1>Hello, {props.name}</h1>;\n'
                '            }\n            ```'
            ),
            expected_lexemes={
                'language': 'jsx',
                'params': {'title': '/src/components/HelloCodeTitle.js'},
                'source': (
                    'function HelloCodeTitle(props) {\n'
                    '  return <h1>Hello, {props.name}</h1>;\n}'
                    '\n'
                ),
            }
        )

.. invisible-code-block: python

  test_docusaurus_lexing()

Once we're confident that the lexer is working as required, we can use it with the existing
:class:`~sybil.parsers.abstract.codeblock.AbstractCodeBlockParser` as follows:

.. code-block:: python

    from sybil.evaluators.python import PythonEvaluator
    from sybil.parsers.abstract.codeblock import AbstractCodeBlockParser

    class DocusaurusCodeBlockParser(AbstractCodeBlockParser):
        def __init__(self) -> None:
            super().__init__(
                lexers=[DocusaurusCodeBlockLexer()],
                language='python',
                evaluator=PythonEvaluator(),
                language_lexeme_name = 'language',
            )

This can then be tested as follows:

.. code-block:: python

    from sybil.testing import check_parser

    def test_docusaurus_parsing() -> None:
        document = check_parser(
            DocusaurusCodeBlockParser(),
            text="""
                ```python title="hello.py"
                x = 1
                ```
            """,
        )
        assert document.namespace['x'] == 1

.. invisible-code-block: python

  test_docusaurus_parsing()
