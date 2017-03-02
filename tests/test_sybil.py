import pytest

from sybil import Document, Region


class TestRegion(object):

    def test_repr(self):
        region = Region(0, 1, 'parsed', 'evaluator')
        assert repr(region) == "<Region start=0 end=1 'evaluator'>"

    def test_evaluate(self):
        def evaluator(parsed, namespace):
            namespace['parsed'] = parsed
        region = Region(0, 1, 'the data', evaluator)
        namespace = {}
        region.evaluate(namespace)
        assert namespace == {'parsed': 'the data'}


@pytest.fixture()
def document():
    return Document('ABCDEFGH')


class TestDocument(object):

    def test_add(self, document):
        region = Region(0, 1, None, None)
        document.add(region)
        assert list(document) == [region]

    def test_add_no_overlap(self, document):
        region1 = Region(0, 1, None, None)
        region2 = Region(6, 8, None, None)
        document.add(region1)
        document.add(region2)
        assert list(document) == [region1, region2]

    def test_add_out_of_order(self, document):
        region1 = Region(0, 1, None, None)
        region2 = Region(6, 8, None, None)
        document.add(region2)
        document.add(region1)
        assert list(document) == [region1, region2]

    def test_add_adjacent(self, document):
        region1 = Region(0, 1, None, None)
        region2 = Region(1, 2, None, None)
        region3 = Region(2, 3, None, None)
        document.add(region1)
        document.add(region3)
        document.add(region2)
        assert list(document) == [region1, region2, region3]

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
