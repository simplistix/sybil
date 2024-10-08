import re
from collections.abc import Iterable, Sequence

from sybil import Document, Region
from sybil.evaluators.skip import Skipper
from sybil.parsers.abstract.lexers import LexerCollection
from sybil.typing import Lexer

SKIP_ARGUMENTS_PATTERN = re.compile(r'(\w+)(?:\s+(.+)$)?')


class AbstractSkipParser:
    """
    An abstract parser for skipping subsequent examples.

    :param lexers:
        A sequence of :any:`Lexer` objects that will be applied in turn to each
        :class:`~sybil.Document` that is parsed.
    """

    def __init__(self, lexers: Sequence[Lexer]):
        self.lexers = LexerCollection(lexers)
        self.skipper = Skipper()

    def __call__(self, document: Document) -> Iterable[Region]:
        for lexed in self.lexers(document):
            arguments = lexed.lexemes['arguments']
            match = SKIP_ARGUMENTS_PATTERN.match(arguments)
            if match is None:
                directive = lexed.lexemes.get('directive', 'skip')
                raise ValueError(f'malformed arguments to {directive}: {arguments!r}')
            yield Region(lexed.start, lexed.end, match.groups(), self.skipper)
