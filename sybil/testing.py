from pathlib import Path

from tempfile import NamedTemporaryFile

from sybil import Sybil


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
