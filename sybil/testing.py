from pathlib import Path

from tempfile import NamedTemporaryFile

from sybil import Sybil, Document
from sybil.typing import Parser, Lexer, LexemeMapping


def check_sybil(sybil: Sybil, text: str) -> Document:
    """
    Run the supplied text through the supplied Sybil instance and evaluate the single
    example it contains.
    """
    with NamedTemporaryFile() as temp:
        temp.write(text.encode())
        temp.flush()
        document = sybil.parse(Path(temp.name))
    examples = list(document.examples())
    assert len(examples) == 1, f'Expected exactly one example, got: {examples}'
    examples[0].evaluate()
    return document


def check_parser(parser: Parser, text: str) -> Document:
    """
    Run the supplied text through the supplied parser and evaluate the single
    example it contains.

    This is for testing :data:`~sybil.typing.Parser` implementations.
    """
    sybil = Sybil(parsers=[parser], pattern='*')
    return check_sybil(sybil, text)
