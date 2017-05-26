import re
from bisect import bisect

from .example import Example


class Document(object):
    """
    This is Sybil's representation of a documentation source file.
    It will be instantiated by Sybil and provided to each parser in turn.
    """

    def __init__(self, text, path):
        #: This is the text of the documentation source file.
        self.text = text
        #: This is the absolute path of the documentation source file.
        self.path = path
        self.end = len(text)
        self.regions = []
        #: This dictionary is the namespace in which all example parsed from
        #: this document will be evaluated.
        self.namespace = {}

    def line_column(self, position):
        line = self.text.count('\n', 0, position)+1
        col = position - self.text.rfind('\n', 0, position)
        return 'line {}, column {}'.format(line, col)

    def raise_overlap(self, *regions):
        reprs = []
        for region in regions:
            reprs.append('{!r} from {} to {}'.format(
                region,
                self.line_column(region.start),
                self.line_column(region.end)
            ))
        raise ValueError('{} overlaps {}'.format(*reprs))

    def add(self, region):
        if region.start < 0:
            raise ValueError('{!r} is before start of document'.format(region))
        if region.end > self.end:
            raise ValueError('{!r} goes beyond end of document'.format(region))
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

    def __iter__(self):
        line = 1
        place = 0
        for _, region in self.regions:
            line += self.text.count('\n', place, region.start)
            line_start = self.text.rfind('\n', place, region.start)
            place = region.start
            yield Example(self,
                          line, region.start-line_start,
                          region, self.namespace)

    def find_region_sources(self, start_pattern, end_pattern):
        """
        This helper method can be called used to extract source text
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
