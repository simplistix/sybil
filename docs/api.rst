.. currentmodule:: sybil

API Reference
=============

This reference is organised into sections relating to the different things you're
likely to be doing when using Sybil.

Sybils
------

.. autoclass:: Sybil
  :members:
  :special-members: __add__

.. autoclass:: sybil.sybil.SybilCollection
  :members:

Documents
---------

.. autoclass:: sybil.Document
  :members:

.. autoclass:: sybil.document.PythonDocument
  :members:

.. autoclass:: sybil.document.PythonDocStringDocument
  :members:

Regions
-------

.. autoclass:: sybil.Region
  :members:

.. autoclass:: sybil.LexedRegion
  :members:

.. autoclass:: sybil.Lexeme
  :members:
  :show-inheritance:

Lexing
------

.. autodata:: sybil.typing.Lexer

.. autoclass:: sybil.parsers.abstract.lexers.BlockLexer

Parsing
-------

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

MyST Parsing and Lexing
-----------------------

.. autoclass:: sybil.parsers.myst.lexers.FencedCodeBlockLexer

.. autoclass:: sybil.parsers.myst.lexers.DirectiveLexer

.. autoclass:: sybil.parsers.myst.lexers.DirectiveInPercentCommentLexer

.. autoclass:: sybil.parsers.myst.lexers.DirectiveInHTMLCommentLexer

.. autoclass:: sybil.parsers.myst.CodeBlockParser
    :inherited-members:

.. autoclass:: sybil.parsers.myst.PythonCodeBlockParser

.. autoclass:: sybil.parsers.myst.DocTestDirectiveParser

.. autoclass:: sybil.parsers.myst.SkipParser

.. autoclass:: sybil.parsers.myst.ClearNamespaceParser

Evaluation
----------

.. automodule:: sybil
  :members: Example

.. autoclass:: sybil.example.NotEvaluated

.. autoclass:: sybil.typing.Evaluator

.. autoclass:: sybil.evaluators.doctest.DocTestEvaluator
