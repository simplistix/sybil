from typing import TYPE_CHECKING, Any

from .region import Region

if TYPE_CHECKING:
    from .document import Document


class SybilFailure(AssertionError):

    def __init__(self, example: 'Example', result: str):
        super(SybilFailure, self).__init__((
            'Example at {}, line {}, column {} did not evaluate as expected:\n'
            '{}'
        ).format(example.path, example.line, example.column, result))
        self.example = example
        self.result = result


class Example:
    """
    This represents a particular example from a documentation source file.
    It is assembled from the :class:`~sybil.document.Document` and 
    :class:`~sybil.Region` the example comes from and is passed to the region's 
    evaluator.
    """

    def __init__(
        self, document: 'Document', line: int, column: int, region: Region, namespace: dict
    ):
        #: The :class:`~sybil.document.Document` from which this example came.
        self.document: 'Document' = document
        #: The absolute path of the :class:`~sybil.document.Document`.
        self.path: str = document.path
        #: The line number at which this example occurs in the
        #: :class:`~sybil.document.Document`.
        self.line: int = line
        #: The column number at which this example occurs in the
        #: :class:`~sybil.document.Document`.
        self.column: int = column
        #: The :class:`~sybil.Region` from which this example came.
        self.region: Region = region
        #: The character position at which this example starts in the
        #: :class:`~sybil.document.Document`.
        self.start: int = region.start
        #: The character position at which this example ends in the
        #: :class:`~sybil.document.Document`.
        self.end: int = region.end
        #: The version of this example provided by the parser that yielded
        #: the :class:`~sybil.Region` containing it.
        self.parsed: Any = region.parsed
        #: The :attr:`~sybil.Document.namespace` of the document from
        #: which this example came.
        self.namespace: dict = namespace

    def __repr__(self) -> str:
        return '<Example path={} line={} column={} using {!r}>'.format(
            self.path, self.line, self.column, self.region.evaluator
        )

    def evaluate(self) -> None:
        evaluator = self.document.evaluator or self.region.evaluator
        result = evaluator(self)
        if result:
            raise SybilFailure(self, result)
