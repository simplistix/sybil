from typing import Iterable

from sybil.evaluators.python import PythonEvaluator
from sybil.parsers.abstract import AbstractCodeBlockParser, DocTestStringParser
from sybil.typing import Evaluator
from .lexers import (
    DirectiveLexer, FencedCodeBlockLexer, DirectiveInPercentCommentLexer,
    DirectiveInHTMLCommentLexer
)
from ... import Document, Region
from ...evaluators.doctest import DocTestEvaluator


class CodeBlockParser(AbstractCodeBlockParser):
    """
    A :any:`Parser` for :ref:`myst-codeblock-parser` examples.

    :param language:
        The language that this parser should look for.

    :param evaluator:
        The evaluator to use for evaluating code blocks in the specified language.
        You can also override the :meth:`evaluate` method below.
    """

    def __init__(self, language: str = None, evaluator: Evaluator = None):
        super().__init__(
            [
                FencedCodeBlockLexer(
                    language=r'.+',
                    mapping={'language': 'arguments', 'source': 'source'},
                ),
                DirectiveLexer(
                    directive='code-block',
                    arguments='.+',
                ),
                DirectiveInPercentCommentLexer(
                    directive=r'(invisible-)?code(-block)?',
                    arguments='.+',
                ),
                DirectiveInHTMLCommentLexer(
                    directive=r'(invisible-)?code(-block)?',
                    arguments='.+',
                ),
            ],
            language, evaluator
        )


class PythonCodeBlockParser(CodeBlockParser):
    """
    A :any:`Parser` for Python :ref:`myst-codeblock-parser` examples.

    :param future_imports:
        An optional list of strings that will be turned into
        ``from __future__ import ...`` statements and prepended to the code
        in each of the examples found by this parser.

    :param doctest_optionflags:
        :ref:`doctest option flags<option-flags-and-directives>` to use
        when evaluating the doctest examples found by this parser.
    """

    language = 'python'

    def __init__(self, future_imports=(), doctest_optionflags=0):
        super().__init__(evaluator=PythonEvaluator(future_imports))
        self.doctest_parser = DocTestStringParser(DocTestEvaluator(doctest_optionflags))

    def __call__(self, document: Document) -> Iterable[Region]:
        for region in super().__call__(document):
            source = region.parsed
            if region.parsed.startswith('>>>'):
                for doctest_region in self.doctest_parser(source, document.path):
                    doctest_region.adjust(region, source)
                    yield doctest_region
            else:
                yield region
