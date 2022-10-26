from typing import Iterable
import re

from sybil import Region, Document
from sybil.evaluators.skip import evaluate_skip

SKIP = re.compile(r'^[ \t]*\.\.\s*skip:\s*(\w+)(?:\s+if(.+)$)?', re.MULTILINE)


def skip(document: Document) -> Iterable[Region]:
    """
    A parser function to be included when your documentation makes use of
    :ref:`skipping <skip-parser>` examples in a document.
    """
    for match in re.finditer(SKIP, document.text):
        yield Region(match.start(), match.end(), match.groups(), evaluate_skip)
