from doctest import (
    DocTestParser as BaseDocTestParser,
    Example as DocTestExample,
)
from typing import Iterable

from sybil.region import Region
from sybil.typing import Evaluator


class DocTestStringParser(BaseDocTestParser):

    def __init__(self, evaluator: Evaluator):
        self.evaluator = evaluator

    def __call__(self, string: str, name: str) -> Iterable[Region]:
        # a cut down version of doctest.DocTestParser.parse:
        # If all lines begin with the same indentation, then strip it.
        min_indent = self._min_indent(string)
        if min_indent > 0:
            string = '\n'.join([l[min_indent:] for l in string.split('\n')])

        charno, lineno = 0, 0
        # Find all doctest examples in the string:
        for m in self._EXAMPLE_RE.finditer(string):
            # Update lineno (lines before this example)
            lineno += string.count('\n', charno, m.start())
            # Extract info from the regexp match.
            source, options, want, exc_msg = self._parse_example(m, name, lineno)

            # Create an Example, and add it to the list.
            if not self._IS_BLANK_OR_COMMENT(source):
                yield Region(
                    m.start(),
                    m.end(),
                    DocTestExample(source, want, exc_msg,
                                   lineno=lineno,
                                   indent=min_indent + len(m.group('indent')),
                                   options=options),
                    self.evaluator

                )
            # Update lineno (lines inside this example)
            lineno += string.count('\n', m.start(), m.end())
            # Update charno.
            charno = m.end()


