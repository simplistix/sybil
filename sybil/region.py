from typing import Dict, Any, Union

from sybil.typing import Parsed, Evaluator


class Lexeme(str):

    def __new__(cls, text: str, line_offset: int):
        return str.__new__(cls, text)

    def __init__(self, text: str, line_offset: int):
        """
        Where needed, this can store both the text of the lexeme
        and it's line offset relative to the line number of the example
        that contains it.
        """
        self.text, self.line_offset = text, line_offset


class LexedRegion:
    """
    A region that has been lexed from a source language but not yet
    parsed to have semantic meaning.
    """

    def __init__(self, start: int, end: int, lexemes: Dict[str, Union[str, Lexeme]]):
        self.start, self.end, self.lexemes = start, end, lexemes


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

    def __init__(self, start: int, end: int, parsed: Parsed, evaluator: Evaluator):
        self.start, self.end, self.parsed, self.evaluator = (
            start, end, parsed, evaluator
        )

    def __repr__(self) -> str:
        return '<Region start={} end={} {!r}>'.format(
            self.start, self.end, self.evaluator
        )

    def __lt__(self, other):
        assert isinstance(other, type(self)), f"{type(other)} not supported for <"
        assert self.start == other.start  # This is where this may happen, if not something weird
        return True
