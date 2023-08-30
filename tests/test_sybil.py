from __future__ import print_function

import re
from functools import partial
from os.path import split
from pathlib import Path

import pytest
from py.path import local

from sybil import Sybil, Region
from sybil.document import Document, PythonDocument
from sybil.example import Example, SybilFailure

from .helpers import sample_path, write_doctest


@pytest.fixture()
def document():
    return Document('ABCDEFGH', '/the/path')


class TestRegion:

    def test_repr(self) -> None:
        region = Region(0, 1, 'parsed', 'evaluator')
        assert repr(region) == "<Region start=0 end=1 'evaluator'>"


class TestExample:

    def test_repr(self, document) -> None:
        region = Region(0, 1, 'parsed', 'evaluator')
        example = Example(document, 1, 2, region, {})
        assert (repr(example) ==
                "<Example path=/the/path line=1 column=2 using 'evaluator'>")

    def test_evaluate_okay(self, document) -> None:
        def evaluator(example):
            example.namespace['parsed'] = example.parsed
        region = Region(0, 1, 'the data', evaluator)
        namespace = {}
        example = Example(document, 1, 2, region, namespace)
        result = example.evaluate()
        assert result is None
        assert namespace == {'parsed': 'the data'}

    def test_evaluate_not_okay(self, document) -> None:
        def evaluator(example):
            return 'foo!'
        region = Region(0, 1, 'the data', evaluator)
        example = Example(document, 1, 2, region, {})
        with pytest.raises(SybilFailure) as excinfo:
            example.evaluate()
        assert str(excinfo.value) == (
            'Example at /the/path, line 1, column 2 did not evaluate as '
            'expected:\nfoo!'
        )
        assert excinfo.value.example is example
        assert excinfo.value.result == 'foo!'

    def test_evaluate_raises_exception(self, document) -> None:
        def evaluator(example):
            raise ValueError('foo!')
        region = Region(0, 1, 'the data', evaluator)
        example = Example(document, 1, 2, region, {})
        with pytest.raises(ValueError) as excinfo:
            example.evaluate()
        assert str(excinfo.value) == 'foo!'


class TestDocument:

    def test_add(self, document) -> None:
        region = Region(0, 1, None, None)
        document.add(region)
        assert [e.region for e in document] == [region]

    def test_add_no_overlap(self, document) -> None:
        region1 = Region(0, 1, None, None)
        region2 = Region(6, 8, None, None)
        document.add(region1)
        document.add(region2)
        assert [e.region for e in document] == [region1, region2]

    def test_add_out_of_order(self, document) -> None:
        region1 = Region(0, 1, None, None)
        region2 = Region(6, 8, None, None)
        document.add(region2)
        document.add(region1)
        assert [e.region for e in document] == [region1, region2]

    def test_add_adjacent(self, document) -> None:
        region1 = Region(0, 1, None, None)
        region2 = Region(1, 2, None, None)
        region3 = Region(2, 3, None, None)
        document.add(region1)
        document.add(region3)
        document.add(region2)
        assert [e.region for e in document] == [region1, region2, region3]

    def test_add_before_start(self, document) -> None:
        region = Region(-1, 0, None, None)
        with pytest.raises(ValueError) as excinfo:
            document.add(region)
        assert str(excinfo.value) == (
            '<Region start=-1 end=0 None> '
            'from line 1, column 0 to line 1, column 1 '
            'is before start of document'
        )

    def test_add_after_end(self, document) -> None:
        region = Region(len(document.text), len(document.text)+1, None, None)
        with pytest.raises(ValueError) as excinfo:
            document.add(region)
        assert str(excinfo.value) == (
            '<Region start=8 end=9 None> '
            'from line 1, column 9 to line 1, column 10 '
            'goes beyond end of document'
        )

    def test_add_overlaps_with_previous(self, document) -> None:
        region1 = Region(0, 2, None, None)
        region2 = Region(1, 3, None, None)
        document.add(region1)
        with pytest.raises(ValueError) as excinfo:
            document.add(region2)
        assert str(excinfo.value) == (
            '<Region start=0 end=2 None>'
            ' from line 1, column 1 to line 1, column 3 overlaps '
            '<Region start=1 end=3 None>'
            ' from line 1, column 2 to line 1, column 4'
        )

    def test_add_at_same_place(self, document) -> None:
        region1 = Region(0, 2, None, None)
        region2 = Region(0, 3, None, None)
        document.add(region1)
        with pytest.raises(ValueError) as excinfo:
            document.add(region2)
        assert str(excinfo.value) == (
            '<Region start=0 end=3 None>'
            ' from line 1, column 1 to line 1, column 4 overlaps '
            '<Region start=0 end=2 None>'
            ' from line 1, column 1 to line 1, column 3'
        )

    def test_add_identical(self, document) -> None:
        region1 = Region(0, 2, None, None)
        region2 = Region(0, 2, None, None)
        document.add(region1)
        with pytest.raises(ValueError) as excinfo:
            document.add(region2)
        assert str(excinfo.value) == (
            '<Region start=0 end=2 None>'
            ' from line 1, column 1 to line 1, column 3 overlaps '
            '<Region start=0 end=2 None>'
            ' from line 1, column 1 to line 1, column 3'
        )

    def test_add_overlaps_with_next(self, document) -> None:
        region1 = Region(0, 1, None, None)
        region2 = Region(1, 3, None, None)
        region3 = Region(2, 4, None, None)
        document.add(region1)
        document.add(region3)
        with pytest.raises(ValueError) as excinfo:
            document.add(region2)
        assert str(excinfo.value) == (
            '<Region start=1 end=3 None> '
            'from line 1, column 2 to line 1, column 4 overlaps '
            '<Region start=2 end=4 None> '
            'from line 1, column 3 to line 1, column 5'
        )

    def test_example_path(self, document) -> None:
        document.add(Region(0, 1, None, None))
        assert [e.document for e in document] == [document]

    def test_example_line_and_column(self) -> None:
        text = 'R1XYZ\nR2XYZ\nR3XYZ\nR4XYZ\nR4XYZ\n'
        i = text.index
        document = Document(text, '')
        document.add(Region(0,         i('R2')+2, None, None))
        document.add(Region(i('R3')-1, i('R3')+2, None, None))
        document.add(Region(i('R4')+3, len(text), None, None))
        assert ([(e.line, e.column) for e in document] ==
                [(1, 1), (2, 6), (4, 4)])


def check(letter, parsed, namespace):
    assert namespace is None
    text, expected = parsed
    assert set(text) == {letter}
    actual = text.count(letter)
    if actual != expected:
        return '{} count was {} instead of {}'.format(
            letter, actual, expected
        )
    # This would normally be wrong, but handy for testing here:
    return '{} count was {}, as expected'.format(letter, actual)


def parse_for_x(document):
    for m in re.finditer(r'(X+) (\d+) check', document.text):
        yield Region(m.start(), m.end(),
                     (m.group(1), int(m.group(2))),
                     partial(check, 'X'))


def parse_for_y(document):
    for m in re.finditer(r'(Y+) (\d+) check', document.text):
        yield Region(m.start(), m.end(),
                     (m.group(1), int(m.group(2))),
                     partial(check, 'Y'))


def evaluate_examples(examples):
    return [e.region.evaluator(e.region.parsed, namespace=None)
            for e in examples]


class TestSybil:

    def test_parse(self) -> None:
        sybil = Sybil([parse_for_x, parse_for_y])
        document = sybil.parse(Path(sample_path('sample1.txt')))
        assert (evaluate_examples(document) ==
                ['X count was 4, as expected',
                 'Y count was 3, as expected'])
        document = sybil.parse(Path(sample_path('sample2.txt')))
        assert (evaluate_examples(document) ==
                ['X count was 3 instead of 4',
                 'Y count was 3, as expected'])

    def test_explicit_encoding(self, tmp_path: Path) -> None:
        path = (tmp_path / 'encoded.txt')
        path.write_text(u'X 1 check\n\xa3', encoding='charmap')
        sybil = Sybil([parse_for_x], encoding='charmap')
        document = sybil.parse(path)
        assert (evaluate_examples(document) ==
                ['X count was 1, as expected'])

    def test_augment_document_mapping(self, tmpdir: local) -> None:

        class TextDocument(Document):
            pass

        sybil = Sybil([], document_types={'.txt': TextDocument})
        document = sybil.parse(write_doctest(tmpdir, 'test.txt'))
        assert type(document) is TextDocument
        document = sybil.parse(write_doctest(tmpdir, 'test.rst'))
        assert type(document) is Document

    def test_override_document_mapping(self) -> None:
        sybil = Sybil([parse_for_x, parse_for_y], document_types={'.py': PythonDocument})
        document = sybil.parse(Path(sample_path('sample1.txt')))
        assert (evaluate_examples(document) ==
                ['X count was 4, as expected',
                 'Y count was 3, as expected'])
        document = sybil.parse(Path(sample_path('comments.py')))
        assert (evaluate_examples(document) ==
                ['X count was 4, as expected',
                 'Y count was 3, as expected'])

    def test_addition(self) -> None:
        rest = Sybil([parse_for_x])
        myst = Sybil([parse_for_y])
        sybil = rest + myst
        assert sybil == [rest, myst]
        # check integrations exist:
        assert sybil.pytest
        assert sybil.unittest

    def test_addition_to_collection(self) -> None:
        rest = Sybil([parse_for_x])
        myst = Sybil([parse_for_y])
        bust = Sybil([parse_for_y])
        sybil = rest + myst
        sybil += [bust]
        assert sybil == [rest, myst, bust]
        # check integrations exist:
        assert sybil.pytest
        assert sybil.unittest


def check_into_namespace(example):
    parsed, namespace = example.region.parsed, example.namespace
    if 'parsed' not in namespace:
        namespace['parsed'] = []
    namespace['parsed'].append(parsed)
    print(namespace['parsed'])


def parse(document):
    for m in re.finditer(r'([XY]+) (\d+) check', document.text):
        yield Region(m.start(), m.end(), m.start(), check_into_namespace)


def test_namespace(capsys) -> None:
    sybil = Sybil([parse], path='./samples')
    documents = [sybil.parse(p) for p in sorted(sybil.path.glob('sample*.txt'))]
    actual = []
    for document in documents:
        for example in document:
            print(split(example.path)[-1], example.line)
            example.evaluate()
            actual.append((
                split(example.path)[-1],
                example.line,
                document.namespace['parsed'].copy(),
            ))
    out, _ = capsys.readouterr()
    assert out.split('\n') == [
        'sample1.txt 1',
        '[0]',
        'sample1.txt 3',
        '[0, 14]',
        'sample2.txt 1',
        '[0]',
        'sample2.txt 3',
        '[0, 13]',
        ''
    ]
