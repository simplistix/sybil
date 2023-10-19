from itertools import chain
from typing import Iterable, Optional, Sequence

from sybil import Document, Region, Example
from sybil.typing import Lexer


class AbstractClearNamespaceParser:
    """
    An abstract parser for clearing the :class:`~sybil.Document.namespace`.
    """

    def __init__(self, lexers: Sequence[Lexer]) -> None:
        self.lexers = lexers

    @staticmethod
    def evaluate(example: Example) -> None:
        example.document.namespace.clear()

    def __call__(self, document: Document) -> Iterable[Region]:
        for lexed in chain(*(lexer(document) for lexer in self.lexers)):
            yield Region(lexed.start, lexed.end, lexed.lexemes['source'], self.evaluate)
