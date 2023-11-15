from sybil.parsers.myst import ClearNamespaceParser, PythonCodeBlockParser
from .helpers import parse


def test_basic():
    examples, namespace = parse(
        'myst-clear.md', PythonCodeBlockParser(), ClearNamespaceParser(), expected=4
    )
    for example in examples:
        example.evaluate()
    assert 'x' not in namespace, namespace
