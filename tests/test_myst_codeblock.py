import __future__
import sys

import pytest
from testfixtures import compare

from sybil import Example
from sybil.parsers.myst import PythonCodeBlockParser, CodeBlockParser
from .helpers import check_excinfo, parse


def test_basic() -> None:
    examples, namespace = parse('myst-codeblock.md', PythonCodeBlockParser(), expected=7)
    namespace['y'] = namespace['z'] = 0
    assert examples[0].evaluate() is None
    assert namespace['y'] == 1
    assert namespace['z'] == 0
    with pytest.raises(Exception) as excinfo:
        examples[1].evaluate()
    compare(examples[1].parsed, expected="raise Exception('boom!')\n", show_whitespace=True)
    assert examples[1].line == 10
    check_excinfo(examples[1], excinfo, 'boom!', lineno=11)
    assert examples[2].evaluate() is None
    assert namespace['y'] == 1
    assert namespace['z'] == 1
    assert examples[3].evaluate() is None
    assert namespace['bin'] == b'x'
    assert namespace['uni'] == u'x'
    assert examples[4].evaluate() is None
    assert 'NoVars' in namespace
    assert examples[5].evaluate() is None
    assert namespace['define_this'] == 1
    assert examples[6].evaluate() is None
    assert 'YesVars' in namespace
    assert '__builtins__' not in namespace


def test_doctest_at_end_of_fenced_codeblock() -> None:
    examples, namespace = parse('myst-codeblock-doctests-end-of-fenced-codeblocks.md',
                                PythonCodeBlockParser(), expected=2)
    assert examples[0].evaluate() is None
    assert examples[1].evaluate() is None
    assert namespace['b'] == 2


def test_other_language_composition_pass() -> None:

    def oh_hai(example: Example) -> None:
        assert isinstance(example, Example)
        assert 'HAI' in example.parsed

    parser = CodeBlockParser(language='lolcode', evaluator=oh_hai)
    examples, namespace = parse('myst-codeblock.md', parser, expected=1)
    assert examples[0].evaluate() is None



def test_other_language_composition_fail() -> None:
    def oh_noez(example: Example) -> None:
        if 'KTHXBYE' in example.parsed:
            raise ValueError('oh noez')

    parser = CodeBlockParser(language='lolcode', evaluator=oh_noez)
    examples, namespace = parse('myst-codeblock.md', parser, expected=1)
    with pytest.raises(ValueError):
        examples[0].evaluate()


def test_other_language_no_evaluator() -> None:
    parser = CodeBlockParser('foo')
    with pytest.raises(NotImplementedError):
        parser.evaluate(...)


class LolCodeCodeBlockParser(CodeBlockParser):

    language = 'lolcode'

    def evaluate(self, example: Example) -> None:
        if example.parsed != 'HAI\n':
            raise ValueError(repr(example.parsed))


def test_other_language_inheritance() -> None:
    examples, namespace = parse('myst-codeblock-lolcode.md', LolCodeCodeBlockParser(), expected=2)
    examples[0].evaluate()
    with pytest.raises(ValueError) as excinfo:
        examples[1].evaluate()
    assert str(excinfo.value) == "'KTHXBYE\\n'"


def future_import_checks(*future_imports):
    parser = PythonCodeBlockParser(future_imports)
    examples, namespace = parse('myst-codeblock-future-imports.md', parser, expected=3)
    with pytest.raises(Exception) as excinfo:
        examples[0].evaluate()
    # check the line number of the first block, which is the hardest case:
    check_excinfo(examples[0], excinfo, 'Boom 1', lineno=3)
    with pytest.raises(Exception) as excinfo:
        examples[1].evaluate()
    # check the line number of the second block:
    check_excinfo(examples[1], excinfo, 'Boom 2', lineno=9)
    examples[2].evaluate()
    # check the line number of the third block:
    assert namespace['foo'].__code__.co_firstlineno == 15
    return namespace['foo']


def test_no_future_imports() -> None:
    future_import_checks()


def test_single_future_import() -> None:
    future_import_checks('barry_as_FLUFL')


def test_multiple_future_imports() -> None:
    future_import_checks('barry_as_FLUFL', 'print_function')


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7 or higher")
def test_functional_future_imports() -> None:
    foo = future_import_checks('annotations')
    # This will keep working but not be an effective test once PEP 563 finally lands:
    assert foo.__code__.co_flags & __future__.annotations.compiler_flag
