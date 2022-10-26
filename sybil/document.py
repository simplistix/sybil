import re
from bisect import bisect
from io import open
from pathlib import Path
from typing import List, Iterable, Pattern, Tuple, Match, Optional

from .example import Example
from .python import import_path
from .region import Region
from .typing import Parser, Evaluator


class Document:
    """
    This is Sybil's representation of a documentation source file.
    It will be instantiated by Sybil and provided to each parser in turn.

    Different types of document can be handled by subclassing to provide the
    required :any:`evaluation <evaluator>`. The required file extensions, such as ``'.py'``,
    can then be mapped to these subclasses using :class:`Sybil's <Sybil>`
    ``document_types`` parameter.
    """

    #: This can be set by :any:`evaluators <Evaluator>` or
    #: :class:`subclasses <sybil.document.PythonDocument>` to affect the evaluation
    #: of future examples. It can be set to a callable that takes an
    #: :class:`~sybil.example.Example`. This callable can then do whatever it needs to do,
    #: including not executing the example at all, modifying the :class:`~sybil.example.Example`
    #: or the :class:`~sybil.document.Document`, or calling the original evaluator on the example.
    #: This last case should always take the form of ``example.region.evaluator(example)``.
    evaluator: Evaluator = None

    def __init__(self, text: str, path: str):
        #: This is the text of the documentation source file.
        self.text: str = text
        #: This is the absolute path of the documentation source file.
        self.path: str = path
        self.end: int = len(text)
        self.regions: List[Tuple[int, Region]] = []
        #: This dictionary is the namespace in which all examples parsed from
        #: this document will be evaluated.
        self.namespace: dict = {}

    @classmethod
    def parse(cls, path: str, *parsers: Parser, encoding: str = 'utf-8') -> 'Document':
        """
        Read the text from the supplied path and parse it into a document
        using the supplied parsers.
        """
        with open(path, encoding=encoding) as source:
            text = source.read()
        document = cls(text, path)
        for parser in parsers:
            for region in parser(document):
                document.add(region)
        return document

    def line_column(self, position: int) -> str:
        """
        Return a line and column location in this document based on a character
        position.
        """
        line = self.text.count('\n', 0, position)+1
        col = position - self.text.rfind('\n', 0, position)
        return 'line {}, column {}'.format(line, col)

    def region_details(self, region: Region) -> str:
        return '{!r} from {} to {}'.format(
            region,
            self.line_column(region.start),
            self.line_column(region.end)
        )

    def raise_overlap(self, *regions: Region) -> None:
        reprs = []
        for region in regions:
            reprs.append(self.region_details(region))
        raise ValueError('{} overlaps {}'.format(*reprs))

    def add(self, region: Region) -> None:
        if region.start < 0:
            raise ValueError('{} is before start of document'.format(
                self.region_details(region)
            ))
        if region.end > self.end:
            raise ValueError('{} goes beyond end of document'.format(
                self.region_details(region)
            ))
        entry = (region.start, region)
        index = bisect(self.regions, entry)
        if index > 0:
            previous = self.regions[index-1][1]
            if previous.end > region.start:
                self.raise_overlap(previous, region)
        if index < len(self.regions):
            next = self.regions[index][1]
            if next.start < region.end:
                self.raise_overlap(region, next)
        self.regions.insert(index, entry)

    def __iter__(self) -> Iterable[Example]:
        line = 1
        place = 0
        for _, region in self.regions:
            line += self.text.count('\n', place, region.start)
            line_start = self.text.rfind('\n', place, region.start)
            place = region.start
            yield Example(self,
                          line, region.start-line_start,
                          region, self.namespace)

    def find_region_sources(
        self, start_pattern: Pattern[str], end_pattern: Pattern[str]
    ) -> Tuple[Match, Match, str]:
        """
        This helper method can be used to extract source text
        for regions based on the two :ref:`regular expressions <re-objects>`
        provided.
        
        It will yield a tuple of ``(start_match, end_match, source)`` for each 
        occurrence of ``start_pattern`` in the document's 
        :attr:`~Document.text` that is followed by an
        occurrence of ``end_pattern``.
        The matches will be provided as :ref:`match objects <match-objects>`,
        while the source is provided as a string.
        """
        for start_match in re.finditer(start_pattern, self.text):
            source_start = start_match.end()
            end_match = end_pattern.search(self.text, source_start)
            source_end = end_match.start()
            source = self.text[source_start:source_end]
            yield start_match, end_match, source


class PythonDocument(Document):
    """
    A :class:`~sybil.Document` type that imports the document's source
    file as a Python module, making names within it available in the document's
    :attr:`~sybil.Document.namespace`.
    """

    def evaluator(self, example: Example) -> Optional[str]:
        """
        Imports the document's source file as a Python module when the first
        :class:`~sybil.example.Example` from it is evaluated.
        """
        module = import_path(Path(self.path))
        self.namespace.update(module.__dict__)
        result = example.region.evaluator(example)
        self.evaluator = None
        return result
