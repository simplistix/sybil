class Region(object):

    def __init__(self, start, end, parsed, evaluator):
        self.start, self.end, self.parsed, self.evaluator = (
            start, end, parsed, evaluator
        )

    def __repr__(self):
        return '<Region start={} end={} {!r}>'.format(
            self.start, self.end, self.evaluator
        )
