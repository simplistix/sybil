from typing import Iterable, Optional

from sybil import Document, Region, Example
from sybil.typing import Lexer


class AbstractClearNamespaceParser:
    """
    An abstract parser for clearing the :class:`~sybil.Document.namespace`.
    """

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer

    @staticmethod
    def evaluate(example: Example) -> None:
        example.document.namespace.clear()

    def __call__(self, document: Document) -> Iterable[Region]:
        for lexed in self.lexer(document):
            yield Region(lexed.start, lexed.end, lexed.lexemes['source'], self.evaluate)
