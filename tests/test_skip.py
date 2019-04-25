from sybil.document import Document
from sybil.parsers.codeblock import CodeBlockParser
from sybil.parsers.skip import skip

from .helpers import sample_path


def test_basic():
    document = Document.parse(sample_path('skip.txt'), CodeBlockParser(), skip)
    for example in document:
        example.evaluate()
    assert document.namespace['run'] == [2, 5]
