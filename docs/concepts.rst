Concepts
========
The following concepts are one's you'll encounter when :doc:`using <use>` Sybil or
writing :doc:`parsers <parsers>` for it:

.. glossary::

  Sybil
    As well as being the name of the project, this is an object that contains
    configuration of :term:`parsers <parser>` and provides :term:`test runner` integration
    for discovering :term:`examples <example>` in :term:`documents <document>` and
    :term:`evaluating <evaluator>` them in the document's :term:`namespace`.

    Its API is defined by :class:`sybil.Sybil`.

    See :doc:`use` and :doc:`integration` for more information.

  Sybil Collection
    When more than one set of configuration is required, :term:`Sybils <Sybil>` can be combined
    using the addition operator to form a single object with a :term:`test runner` integration.

    The API is defined by :class:`sybil.sybil.SybilCollection` and :any:`sybil.Sybil.__add__`.

    See :doc:`patterns`.

  Document
    An object representing a file in the project containing :term:`examples <example>`
    that need to be :term:`evaluated <evaluator>`.

    Its API is defined by :class:`sybil.Document`.

    See :doc:`use` for more information.

  Region
    An object representing a region in a :term:`document` containing exactly one
    :term:`example` that needs to be :term:`evaluated <evaluator>`.

    Within a single :term:`Sybil`, no region may overlap with another. This is to ensure
    that :term:`examples <example>` can be executed in a consistent order, and also helps
    to highlight :doc:`parsing <parsers>` errors, which often result in overlapping
    regions.

    The API is defined by :class:`sybil.Region`.

    See :doc:`use` and :doc:`parsers` for more information.

  Test Runner
    Sybil works by integrating with the test runner used by your project.
    This is done by using the appropriate integration method on the :term:`Sybil` or
    :term:`Sybil Collection`.

    See :doc:`test runner integration <integration>` for more information.

  Lexer
    Different documentation and source formats often result in the same type of
    :term:`examples <example>`. However, they have their own concepts such as
    :class:`directives <sybil.parsers.rest.lexers.DirectiveLexer>` in ReST and
    :class:`fenced code blocks <sybil.parsers.markdown.lexers.FencedCodeBlockLexer>` in Markdown.

    A lexer is a callable that takes a :term:`document` and yields a sequence of
    :term:`regions <Region>` that do not have the :attr:`~sybil.Region.parsed` or
    :attr:`~sybil.Region.evaluator` attributes set.

    These allow :term:`parsers <parser>` and :term:`evaluators <evaluator>` to have
    simpler implementations that are common across different source formats and
    can make life easier when writing new :term:`parsers <parser>` for an
    existing source format.

    Its API is defined by :class:`sybil.typing.Lexer`.

    See :doc:`parsers` for more information.

  Parser
    A callable that takes a :term:`document` and yields a sequence of :term:`regions <Region>`.
    Parsers may user :term:`lexers <Lexer>` to turn text in specific text formats into abstract
    primitives such as :class:`blocks <sybil.parsers.abstract.lexers.BlockLexer>`.

    Its API is defined by :any:`sybil.typing.Parser`.

    See :doc:`use` and :doc:`parsers` for more information.

  Example
    An objecting representing an example in a :term:`document`.
    It collects information from both the :term:`document` and the :term:`region`
    and knows how to evaluate itself using any applicable :term:`evaluators <evaluator>`
    from either the :term:`region` or :term:`document` it came from.

    Its API is defined by :any:`sybil.example.Example`.

    See :doc:`use` and :doc:`parsers` for more information.

  Namespace
    This is a :class:`dict` in which all :term:`examples <example>` in a :term:`document`
    will be :term:`evaluated <evaluator>`. Namespaces are not shared between
    :term:`documents <document>`.

    For :any:`python <sybil.evaluators.python.PythonEvaluator>` or
    :any:`doctest <sybil.evaluators.doctest.DocTestEvaluator>` evaluation, this is
    used for :any:`globals`, and for other :term:`evaluators <evaluator>` it can
    be used to store state or provide named objects for use in the evaluation of
    other examples.

    Its API is defined by :class:`sybil.Document.namespace`

    See :doc:`use` and :doc:`parsers` for more information.

  Evaluator
    A callable that takes an :term:`example` and can raise an :class:`Exception` or
    return a :class:`str` to indicate that the example was not successfully evaluated.

    It will often use or modify the :term:`namespace`.

    Its API is defined by :any:`sybil.typing.Evaluator`.

    See :doc:`use` and :doc:`parsers` for more information.
