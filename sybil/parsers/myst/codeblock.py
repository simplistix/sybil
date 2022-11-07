from sybil.evaluators.python import PythonEvaluator
from sybil.parsers.abstract import AbstractCodeBlockParser
from sybil.typing import Evaluator
from .lexers import (
    DirectiveLexer, FencedCodeBlockLexer, DirectiveInPercentCommentLexer,
    DirectiveInHTMLCommentLexer
)


class CodeBlockParser(AbstractCodeBlockParser):
    """
    A class to instantiate and include when your documentation makes use of
    :ref:`codeblock-parser` examples.

    :param language:
        The language that this parser should look for.

    :param evaluator:
        The evaluator to use for evaluating code blocks in the specified language.
        You can also override the :meth:`evaluate` below.
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
    A class to instantiate and include when your documentation makes use of
    Python :ref:`codeblock-parser` examples.

    :param future_imports:
        An optional list of strings that will be turned into
        ``from __future__ import ...`` statements and prepended to the code
        in each of the examples found by this parser.
    """

    def __init__(self, future_imports=()):
        super().__init__(language='python', evaluator=PythonEvaluator(future_imports))
