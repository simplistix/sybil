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


def check_lexer(
    lexer: Lexer, source_text: str, expected_text: str, expected_lexemes: LexemeMapping
) -> None:
    """
    Run the supplied text through the supplied lexer make sure it lexes a single
    region and captures the expected text and lexemes.

    This is for testing :data:`~sybil.typing.Lexer` implementations.
    """
    document = Document(source_text, 'sample.txt')
    regions = list(lexer(document))
    assert len(regions) == 1, f'Expected exactly one region, got: {regions}'
    region = regions[0]
    assert expected_text == document.text[region.start:region.end]
    assert region.lexemes == expected_lexemes
