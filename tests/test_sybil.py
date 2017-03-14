import pytest

from sybil import Document, Region, Example


@pytest.fixture()
def document():
    return Document('ABCDEFGH', '/the/path')


class TestRegion(object):

    def test_repr(self):
        region = Region(0, 1, 'parsed', 'evaluator')
        assert repr(region) == "<Region start=0 end=1 'evaluator'>"


class TestExample(object):

    def test_repr(self):
        region = Region(0, 1, 'parsed', 'evaluator')
        example = Example('/the/path', 1, 2, region)
        assert (repr(example) ==
                "<Example path=/the/path line=1 column=2 using 'evaluator'>")

    def test_evaluate(self):
        def evaluator(parsed, namespace):
            namespace['parsed'] = parsed
            return 'foo!'
        region = Region(0, 1, 'the data', evaluator)
        example = Example('/the/path', 1, 2, region)
        namespace = {}
        result = example.evaluate(namespace)
        assert result == 'foo!'
        assert namespace == {'parsed': 'the data'}


class TestDocument(object):

    def test_add(self, document):
        region = Region(0, 1, None, None)
        document.add(region)
        assert [e.region for e in document] == [region]

    def test_add_no_overlap(self, document):
        region1 = Region(0, 1, None, None)
        region2 = Region(6, 8, None, None)
        document.add(region1)
        document.add(region2)
        assert [e.region for e in document] == [region1, region2]

    def test_add_out_of_order(self, document):
        region1 = Region(0, 1, None, None)
        region2 = Region(6, 8, None, None)
        document.add(region2)
        document.add(region1)
        assert [e.region for e in document] == [region1, region2]

    def test_add_adjacent(self, document):
        region1 = Region(0, 1, None, None)
        region2 = Region(1, 2, None, None)
        region3 = Region(2, 3, None, None)
        document.add(region1)
        document.add(region3)
        document.add(region2)
        assert [e.region for e in document] == [region1, region2, region3]

    def test_add_before_start(self, document):
        region = Region(-1, 0, None, None)
        with pytest.raises(ValueError) as excinfo:
            document.add(region)
        assert str(excinfo.value) == (
            '<Region start=-1 end=0 None> is before start of document'
        )

    def test_add_after_end(self, document):
        region = Region(len(document.text), len(document.text)+1, None, None)
        with pytest.raises(ValueError) as excinfo:
            document.add(region)
        assert str(excinfo.value) == (
            '<Region start=8 end=9 None> goes beyond end of document'
        )

    def test_add_overlaps_with_previous(self, document):
        region1 = Region(0, 2, None, None)
        region2 = Region(1, 3, None, None)
        document.add(region1)
        with pytest.raises(ValueError) as excinfo:
            document.add(region2)
        assert str(excinfo.value) == (
            '<Region start=0 end=2 None> overlaps <Region start=1 end=3 None>'
        )

    def test_add_overlaps_with_next(self, document):
        region1 = Region(0, 1, None, None)
        region2 = Region(1, 3, None, None)
        region3 = Region(2, 4, None, None)
        document.add(region1)
        document.add(region3)
        with pytest.raises(ValueError) as excinfo:
            document.add(region2)
        assert str(excinfo.value) == (
            '<Region start=1 end=3 None> overlaps <Region start=2 end=4 None>'
        )

    def test_example_path(self, document):
        document.add(Region(0, 1, None, None))
        assert [e.path for e in document] == ['/the/path']

    def test_example_line_and_column(self):
        text = 'R1XYZ\nR2XYZ\nR3XYZ\nR4XYZ\nR4XYZ\n'
        i = text.index
        document = Document(text, '')
        document.add(Region(0,         i('R2')+2, None, None))
        document.add(Region(i('R3')-1, i('R3')+2, None, None))
        document.add(Region(i('R4')+3, len(text), None, None))
        assert ([(e.line, e.column) for e in document] ==
                [(1, 1), (2, 6), (4, 4)])
