class Region(object):
    """
    Parsers should yield instances of this class for each example they
    discover in a documentation source file.
    
    :param start: 
        The character position at which the example starts in the
        :class:`~sybil.document.Document`.
    
    :param end: 
        The character position at which the example ends in the
        :class:`~sybil.document.Document`.
    
    :param parsed: 
        The parsed version of the  example.
    
    :param evaluator: 
        The callable to use to evaluate this example and check if it is
        as it should be.
    """

    def __init__(self, start, end, parsed, evaluator):
        self.start, self.end, self.parsed, self.evaluator = (
            start, end, parsed, evaluator
        )

    def __repr__(self):
        return '<Region start={} end={} {!r}>'.format(
            self.start, self.end, self.evaluator
        )
