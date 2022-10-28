import re
from typing import Iterable, Pattern

from sybil import Document, Region
from sybil.evaluators.skip import evaluate_skip


class AbstractSkipParser:

    pattern: Pattern

    def __call__(self, document: Document) -> Iterable[Region]:
        for match in re.finditer(self.pattern, document.text):
            yield Region(match.start(), match.end(), match.groups(), evaluate_skip)
