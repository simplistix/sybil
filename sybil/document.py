from bisect import bisect

from .example import Example


class Document(object):

    def __init__(self, text, path):
        self.text = text
        self.path = path
        self.end = len(text)
        self.regions = []
        self.namespace = {}

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
                raise ValueError('{!r} overlaps {!r}'.format(previous, region))
        if index < len(self.regions):
            next = self.regions[index][1]
            if next.start < region.end:
                raise ValueError('{!r} overlaps {!r}'.format(region, next))
        self.regions.insert(index, entry)

    def __iter__(self):
        line = 1
        place = 0
        for _, region in self.regions:
            line += self.text.count('\n', place, region.start)
            line_start = self.text.rfind('\n', place, region.start)
            place = region.start
            yield Example(self.path,
                          line, region.start-line_start,
                          region, self.namespace)
