from sybil.parsers.rest import ClearNamespaceParser, DocTestParser
from .helpers import parse


def test_basic():
    examples, namespace = parse('clear.txt', DocTestParser(), ClearNamespaceParser(), expected=4)
    for example in examples:
        example.evaluate()
    assert 'x' not in namespace, namespace
