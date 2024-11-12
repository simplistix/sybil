.. currentmodule:: sybil

API Reference
=============

This reference is organised into sections relating to the different :doc:`concepts <concepts>`
you're likely to encounter when using Sybil.

Sybils
------

See the :term:`Sybil` concept definition for information.

.. autoclass:: Sybil
  :members:
  :special-members: __add__

.. autoclass:: sybil.sybil.SybilCollection
  :members:

Documents
---------

See the :term:`Document` concept definition for information.

.. autoclass:: sybil.Document
  :members:

.. autoclass:: sybil.document.PythonDocument
  :members:

.. autoclass:: sybil.document.PythonDocStringDocument
  :members:

Regions
-------

See the :term:`Region` concept definition for information.

.. autoclass:: sybil.Region
  :members:

.. autoclass:: sybil.Lexeme
  :members:
  :show-inheritance:

Lexing
------

See the :term:`Lexer` concept definition for information.

.. autodata:: sybil.typing.Lexer

.. autodata:: sybil.typing.LexemeMapping

.. autoclass:: sybil.parsers.abstract.lexers.BlockLexer

.. autoclass:: sybil.parsers.abstract.lexers.LexingException

Parsing
-------

See the :term:`Parser` concept definition for information.

.. autodata:: sybil.typing.Parser

.. autoclass:: sybil.parsers.abstract.codeblock.AbstractCodeBlockParser
    :members:

.. autoclass:: sybil.parsers.abstract.doctest.DocTestStringParser
    :members: __call__, evaluator

.. autoclass:: sybil.parsers.abstract.skip.AbstractSkipParser
    :members:

.. autoclass:: sybil.parsers.abstract.clear.AbstractClearNamespaceParser


ReST Parsing and Lexing
-----------------------

See the :term:`Lexer` and :term:`Parser` concept definitions for information.

.. autoclass:: sybil.parsers.rest.lexers.DirectiveLexer

.. autoclass:: sybil.parsers.rest.lexers.DirectiveInCommentLexer

.. autoclass:: sybil.parsers.rest.CaptureParser

.. autoclass:: sybil.parsers.rest.CodeBlockParser
    :inherited-members:
    :exclude-members: pad

.. autoclass:: sybil.parsers.rest.PythonCodeBlockParser

.. autoclass:: sybil.parsers.rest.DocTestParser

.. autoclass:: sybil.parsers.rest.DocTestDirectiveParser

.. autoclass:: sybil.parsers.rest.SkipParser

.. autoclass:: sybil.parsers.rest.ClearNamespaceParser

Markdown Parsing and Lexing
---------------------------

See the :term:`Lexer` and :term:`Parser` concept definitions for information.

.. autoclass:: sybil.parsers.markdown.lexers.RawFencedCodeBlockLexer

.. autoclass:: sybil.parsers.markdown.lexers.FencedCodeBlockLexer

.. autoclass:: sybil.parsers.markdown.lexers.DirectiveInHTMLCommentLexer

.. autoclass:: sybil.parsers.markdown.CodeBlockParser
    :inherited-members:

.. autoclass:: sybil.parsers.markdown.PythonCodeBlockParser

.. autoclass:: sybil.parsers.markdown.SkipParser

.. autoclass:: sybil.parsers.markdown.ClearNamespaceParser

MyST Parsing and Lexing
-----------------------

See the :term:`Lexer` and :term:`Parser` concept definitions for information.

.. autoclass:: sybil.parsers.myst.lexers.DirectiveLexer

.. autoclass:: sybil.parsers.myst.lexers.DirectiveInPercentCommentLexer

.. autoclass:: sybil.parsers.myst.CodeBlockParser
    :inherited-members:

.. autoclass:: sybil.parsers.myst.PythonCodeBlockParser

.. autoclass:: sybil.parsers.myst.DocTestDirectiveParser

.. autoclass:: sybil.parsers.myst.SkipParser

.. autoclass:: sybil.parsers.myst.ClearNamespaceParser

Evaluation
----------

See the :term:`Evaluator` concept definition for information.

.. automodule:: sybil
  :members: Example

.. autoclass:: sybil.example.NotEvaluated

.. autoclass:: sybil.typing.Evaluator

.. autoclass:: sybil.evaluators.doctest.DocTestEvaluator

.. autoclass:: sybil.evaluators.python.PythonEvaluator
