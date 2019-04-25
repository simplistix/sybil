class SybilFailure(AssertionError):

    def __init__(self, example, result):
        super(SybilFailure, self).__init__((
            'Example at {}, line {}, column {} did not evaluate as expected:\n'
            '{}'
        ).format(example.document.path, example.line, example.column, result))
        self.example = example
        self.result = result


class Example(object):
    """
    This represents a particular example from a documentation source file.
    It is assembled from the :class:`~sybil.document.Document` and 
    :class:`~sybil.Region` the example comes from and is passed to the region's 
    evaluator.
    """

    def __init__(self, document, line, column, region, namespace):
        #: The :class:`~sybil.document.Document` from which this example came.
        self.document = document
        #: The absolute path of the :class:`~sybil.document.Document`.
        self.path = document.path
        #: The line number at which this example occurs in the
        #: :class:`~sybil.document.Document`.
        self.line = line
        #: The column number at which this example occurs in the
        #: :class:`~sybil.document.Document`.
        self.column = column
        #: The :class:`~sybil.Region` from which this example came.
        self.region = region
        #: The character position at which this example starts in the
        #: :class:`~sybil.document.Document`.
        self.start = region.start
        #: The character position at which this example ends in the
        #: :class:`~sybil.document.Document`.
        self.end = region.end
        #: The version of this example provided by the parser that yielded
        #: the :class:`~sybil.Region` containing it.
        self.parsed = region.parsed
        #: The :attr:`~sybil.document.Document.namespace` of the document from
        #: which this example came.
        self.namespace = namespace

    def __repr__(self):
        return '<Example path={} line={} column={} using {!r}>'.format(
            self.document.path, self.line, self.column, self.region.evaluator
        )

    def evaluate(self):
        evaluator = self.document.evaluator or self.region.evaluator
        result = evaluator(self)
        if result:
            raise SybilFailure(self, result)
