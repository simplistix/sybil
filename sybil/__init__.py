from bisect import bisect


class Document(object):

    def __init__(self, text, path):
        self.text = text
        self.path = path
        self.end = len(text)
        self.regions = []

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
        for _, region in self.regions:
            yield region


class Region(object):

    def __init__(self, start, end, parsed, evaluator):
        self.start, self.end, self.parsed, self.evaluator = (
            start, end, parsed, evaluator
        )

    def __repr__(self):
        return '<Region start={} end={} {!r}>'.format(
            self.start, self.end, self.evaluator
        )

    def evaluate(self, namespace):
        self.evaluator(self.parsed, namespace)
