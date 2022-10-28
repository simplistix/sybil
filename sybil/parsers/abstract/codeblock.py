from itertools import chain
from typing import Iterable, Sequence

from sybil import Region, Document, Example
from sybil.typing import Evaluator, Lexer


class AbstractCodeBlockParser:
    """
    A class to instantiate and include when your documentation makes use of
    :ref:`codeblock-parser` examples.

    :param language:
        The language that this parser should look for.

    :param evaluator:
        The evaluator to use for evaluating code blocks in the specified language.
        You can also override the :meth:`evaluate` below.
    """

    language: str

    def __init__(self, lexers: Sequence[Lexer], language: str = None, evaluator: Evaluator = None):
        self.lexers = lexers
        if language is not None:
            self.language = language
        assert self.language, 'language must be specified!'
        if evaluator is not None:
            self.evaluate = evaluator

    def evaluate(self, example: Example):
        raise NotImplementedError

    def __call__(self, document: Document) -> Iterable[Region]:
        for lexed in chain(*(lexer(document) for lexer in self.lexers)):
            if lexed.lexemes['arguments'] == self.language:
                yield Region(lexed.start, lexed.end, lexed.lexemes['source'], self.evaluate)
