from typing import Dict, Any, Union

from sybil.typing import Evaluator


class Lexeme(str):
    """
    Where needed, this can store both the text of the lexeme
    and it's line offset relative to the line number of the example
    that contains it.
    """

    def __new__(cls, text: str, offset, line_offset: int):
        return str.__new__(cls, text)

    def __init__(self, text: str, offset, line_offset: int):
        self.text, self.offset, self.line_offset = text, offset, line_offset


class LexedRegion:
    """
    A region that has been lexed from a source language but not yet
    parsed or assigned an :any:`Evaluator`.
    """

    def __init__(self, start: int, end: int, lexemes: Dict[str, Union[str, Lexeme]]):
        #: The start of this lexed region within the document's :attr:`~sybil.Document.text`.
        self.start: int = start
        #: The end of this lexed region within the document's :attr:`~sybil.Document.text`.
        self.end: int = end
        #: The lexemes extracted from the region.
        self.lexemes: Dict[str, Union[str, Lexeme]] = lexemes


class Region:
    """
    Parsers should yield instances of this class for each example they
    discover in a documentation source file.
    
    :param start: 
        The character position at which the example starts in the
        :class:`~sybil.document.Document`.
    
    :param end: 
        The character position at which the example ends in the
        :class:`~sybil.document.Document`.
    
    :param parsed: 
        The parsed version of the example.
    
    :param evaluator: 
        The callable to use to evaluate this example and check if it is
        as it should be.
    """

    def __init__(self, start: int, end: int, parsed: Any, evaluator: Evaluator):
        #: The start of this region within the document's :attr:`~sybil.Document.text`.
        self.start: int = start
        #: The end of this region within the document's :attr:`~sybil.Document.text`.
        self.end: int = end
        #: The parsed version of this region. This only needs to have meaning to
        #: the :attr:`evaluator`.
        self.parsed: Any = parsed
        #: The :any:`Evaluator` for this region.
        self.evaluator: Evaluator = evaluator

    def __repr__(self) -> str:
        return '<Region start={} end={} {!r}>'.format(
            self.start, self.end, self.evaluator
        )

    def __lt__(self, other):
        assert isinstance(other, type(self)), f"{type(other)} not supported for <"
        assert self.start == other.start  # This is where this may happen, if not something weird
        return True

    def adjust(self, lexed: Union['Region', 'LexedRegion'], lexeme: Lexeme):
        """
        Adjust the start and end of this region based on the provided :class:`Lexeme`
        and :class:`LexedRegion` or :class:`Region` that lexeme came from.
        """
        self.start += (lexed.start + lexeme.offset)
        self.end += lexed.start
