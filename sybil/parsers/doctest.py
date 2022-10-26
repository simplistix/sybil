from doctest import (
    DocTestParser as BaseDocTestParser,
    Example as DocTestExample,
)
from typing import Iterable

from .. import Document
from ..evaluators.doctest import DocTestEvaluator
from ..region import Region


class DocTestParser(BaseDocTestParser):
    """
    A class to instantiate and include when your documentation makes use of
    :ref:`doctest-parser` examples.
     
    :param optionflags: 
        :ref:`doctest option flags<option-flags-and-directives>` to use
        when evaluating the examples found by this parser.

    """
    def __init__(self, optionflags=0):
        self.evaluator = DocTestEvaluator(optionflags)

    def __call__(self, document: Document) -> Iterable[Region]:
        # a cut down version of doctest.DocTestParser.parse:

        text = document.text
        # If all lines begin with the same indentation, then strip it.
        min_indent = self._min_indent(text)
        if min_indent > 0:
            text = '\n'.join([l[min_indent:] for l in text.split('\n')])

        charno, lineno = 0, 0
        # Find all doctest examples in the string:
        for m in self._EXAMPLE_RE.finditer(text):
            # Update lineno (lines before this example)
            lineno += text.count('\n', charno, m.start())
            # Extract info from the regexp match.
            source, options, want, exc_msg = self._parse_example(m, document.path, lineno)

            # Create an Example, and add it to the list.
            if not self._IS_BLANK_OR_COMMENT(source):
                yield Region(
                    m.start(),
                    m.end(),
                    DocTestExample(source, want, exc_msg,
                                   lineno=lineno,
                                   indent=min_indent+len(m.group('indent')),
                                   options=options),
                    self.evaluator

                )
            # Update lineno (lines inside this example)
            lineno += text.count('\n', m.start(), m.end())
            # Update charno.
            charno = m.end()
