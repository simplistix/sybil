from sybil.parsers.myst import PythonCodeBlockParser, SkipParser
from .helpers import parse


def test_basic():
    examples, namespace = parse('myst-skip.md', PythonCodeBlockParser(), SkipParser(), expected=9)
    for example in examples:
        example.evaluate()
    assert namespace['run'] == [2, 5]
