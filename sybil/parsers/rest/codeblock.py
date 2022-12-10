from sybil.evaluators.python import pad, PythonEvaluator
from sybil.parsers.abstract import AbstractCodeBlockParser
from sybil.parsers.rest.lexers import DirectiveLexer, DirectiveInCommentLexer
from sybil.typing import Evaluator


class CodeBlockParser(AbstractCodeBlockParser):
    """
    A :any:`Parser` for :ref:`codeblock-parser` examples.

    :param language:
        The language that this parser should look for.

    :param evaluator:
        The evaluator to use for evaluating code blocks in the specified language.
        You can also override the :meth:`evaluate` method below.
    """

    def __init__(self, language: str = None, evaluator: Evaluator = None):
        super().__init__(
            [
                DirectiveLexer(directive=r'code-block'),
                DirectiveInCommentLexer(directive=r'(invisible-)?code(-block)?'),
            ],
            language, evaluator
        )

    pad = staticmethod(pad)


class PythonCodeBlockParser(CodeBlockParser):
    """
    A :any:`Parser` for Python :ref:`codeblock-parser` examples.

    :param future_imports:
        An optional list of strings that will be turned into
        ``from __future__ import ...`` statements and prepended to the code
        in each of the examples found by this parser.
    """

    def __init__(self, future_imports=()):
        super().__init__(language='python', evaluator=PythonEvaluator(future_imports))
