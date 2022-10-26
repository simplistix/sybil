from itertools import chain
from typing import Iterable, Sequence, Optional

from sybil import Region, Document, Example
from sybil.typing import Evaluator, Lexer


class AbstractCodeBlockParser:
    """
    An abstract parser for use when evaluating blocks of code.

    :param lexers:
        A sequence of :any:`Lexer` objects that will be applied in turn to each
        :class:`~sybil.Document`
        that is parsed. The :class:`~sybil.LexedRegion` objects returned by these lexers must have
        both an ``arguments`` string, containing the language of the lexed region, and a
        ``source`` :class:`~sybil.Lexeme` containing the source code of the lexed region.

    :param language:
        The language that this parser should look for. Lexed regions which don't have this
        language in their ``arguments`` lexeme will be ignored.

    :param evaluator:
        The evaluator to use for evaluating code blocks in the specified language.
        You can also override the :meth:`evaluate` method below.
    """

    language: str

    def __init__(self, lexers: Sequence[Lexer], language: str = None, evaluator: Evaluator = None):
        self.lexers = lexers
        if language is not None:
            self.language = language
        assert self.language, 'language must be specified!'
        if evaluator is not None:
            self.evaluate = evaluator

    def evaluate(self, example: Example) -> Optional[str]:
        """
        The :any:`Evaluator` used for regions yields by this parser can be provided by
        implementing this method.
        """
        raise NotImplementedError

    def __call__(self, document: Document) -> Iterable[Region]:
        for lexed in chain(*(lexer(document) for lexer in self.lexers)):
            if lexed.lexemes['arguments'] == self.language:
                yield Region(lexed.start, lexed.end, lexed.lexemes['source'], self.evaluate)
