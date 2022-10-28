from typing import Iterable

from sybil import Document, Region
from sybil.evaluators.doctest import DocTestEvaluator
from sybil.parsers.abstract import DocTestStringParser


class DocTestParser:
    """
    A class to instantiate and include when your documentation makes use of
    :ref:`doctest-parser` examples.

    :param optionflags:
        :ref:`doctest option flags<option-flags-and-directives>` to use
        when evaluating the examples found by this parser.

    """
    def __init__(self, optionflags=0):
        self.string_parser = DocTestStringParser(DocTestEvaluator(optionflags))

    def __call__(self, document: Document) -> Iterable[Region]:
        return self.string_parser(document.text, document.path)
