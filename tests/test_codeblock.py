import __future__
import sys
from pathlib import Path

import pytest
from testfixtures import compare

from sybil import Example, Sybil, Region
from sybil.document import Document
from sybil.parsers.codeblock import PythonCodeBlockParser, CodeBlockParser
from .helpers import check_excinfo, parse, sample_path, check_path, SAMPLE_PATH, add_to_python_path


def test_basic():
    examples, namespace = parse('codeblock.txt', PythonCodeBlockParser(), expected=7)
    namespace['y'] = namespace['z'] = 0
    assert examples[0].evaluate() is None
    assert namespace['y'] == 1
    assert namespace['z'] == 0
    with pytest.raises(Exception) as excinfo:
        examples[1].evaluate()
    compare(examples[1].parsed, expected="raise Exception('boom!')\n", show_whitespace=True)
    assert examples[1].line == 9
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


def test_other_language_composition_pass():

    def oh_hai(example):
        assert isinstance(example, Example)
        assert 'HAI' in example.parsed

    parser = CodeBlockParser(language='lolcode', evaluator=oh_hai)
    examples, namespace = parse('codeblock.txt', parser, expected=1)
    assert examples[0].evaluate() is None


def test_other_language_composition_fail():
    def oh_noez(example):
        if 'KTHXBYE' in example.parsed:
            raise ValueError('oh noez')

    parser = CodeBlockParser(language='lolcode', evaluator=oh_noez)
    examples, namespace = parse('codeblock.txt', parser, expected=1)
    with pytest.raises(ValueError):
        examples[0].evaluate()


def test_other_language_no_evaluator():
    parser = CodeBlockParser('foo')
    with pytest.raises(NotImplementedError):
        parser.evaluate(...)


class LolCodeCodeBlockParser(CodeBlockParser):

    language = 'lolcode'

    def evaluate(self, example: Example):
        if example.parsed != 'HAI\n':
            raise ValueError(repr(example.parsed))


def test_other_language_inheritance():
    examples, namespace = parse('codeblock_lolcode.txt', LolCodeCodeBlockParser(), expected=2)
    examples[0].evaluate()
    with pytest.raises(ValueError) as excinfo:
        examples[1].evaluate()
    assert str(excinfo.value) == "'KTHXBYE'"


class IgnoringPythonCodeBlockParser(PythonCodeBlockParser):

    def __call__(self, document):
        for region in super().__call__(document):
            options = region.lexemes.get('options')
            if options and 'ignore' in options:
                region.evaluator = None
            yield region


def test_other_functionality_inheritance():
    examples, namespace = parse(
        'codeblock-subclassing.txt', IgnoringPythonCodeBlockParser(), expected=2
    )
    examples[0].evaluate()
    examples[1].evaluate()


def future_import_checks(*future_imports):
    parser = PythonCodeBlockParser(future_imports)
    examples, namespace = parse('codeblock_future_imports.txt', parser, expected=3)
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


def test_no_future_imports():
    future_import_checks()


def test_single_future_import():
    future_import_checks('barry_as_FLUFL')


def test_multiple_future_imports():
    future_import_checks('barry_as_FLUFL', 'print_function')


def test_functional_future_imports():
    foo = future_import_checks('annotations')
    # This will keep working but not be an effective test once PEP 563 finally lands:
    assert foo.__code__.co_flags & __future__.annotations.compiler_flag


def test_windows_line_endings(tmp_path: Path):
    p = tmp_path / "example.txt"
    p.write_bytes(
        b'This is my example:\r\n\r\n'
        b'.. code-block:: python\r\n\r\n'
        b'    from math import cos\r\n'
        b'    x = 123\r\n\r\n'
        b'That was my example.\r\n'
    )
    document = Document.parse(str(p), PythonCodeBlockParser())
    example, = document
    example.evaluate()
    assert document.namespace['x'] == 123


def test_line_numbers_with_options():
    parser = PythonCodeBlockParser()
    examples, namespace = parse('codeblock_with_options.txt', parser, expected=2)
    with pytest.raises(Exception) as excinfo:
        examples[0].evaluate()
    # check the line number of the first block, which is the hardest case:
    check_excinfo(examples[0], excinfo, 'Boom 1', lineno=6)
    with pytest.raises(Exception) as excinfo:
        examples[1].evaluate()
    # check the line number of the second block:
    check_excinfo(examples[1], excinfo, 'Boom 2', lineno=14)


def test_codeblocks_in_docstrings():
    sybil = Sybil([PythonCodeBlockParser()])
    with add_to_python_path(SAMPLE_PATH):
        check_path(sample_path('docstrings.py'), sybil, expected=3)
