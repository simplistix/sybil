import re
from bisect import bisect

from .example import Example


class Document(object):

    def __init__(self, text, path):
        self.text = text
        self.path = path
        self.end = len(text)
        self.regions = []
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
        for start_match in re.finditer(start_pattern, self.text):
            source_start = start_match.end()
            end_match = end_pattern.search(self.text, source_start)
            source_end = end_match.start()
            source = self.text[source_start:source_end]
            yield start_match, end_match, source
