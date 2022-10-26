import re
from typing import Iterable, Pattern

from sybil import Document, Region
from sybil.evaluators.skip import evaluate_skip


class AbstractSkipParser:
    """
    An abstract parser for skipping subsequent examples.
    """

    #: Must return :class:`matches<typing.Match>` that contain two groups;
    #: group 1 containing an action of ``'next'``, ``'start'`` or ``'end'`` and group 2
    #: which should contain the source for an optional parenthesis-surrounded Python expression.
    pattern: Pattern

    def __call__(self, document: Document) -> Iterable[Region]:
        for match in re.finditer(self.pattern, document.text):
            yield Region(match.start(), match.end(), match.groups(), evaluate_skip)
