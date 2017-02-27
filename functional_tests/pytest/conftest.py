import pytest


class DummyFile(pytest.File):
    def collect(self):
        yield DummyItem(self, self)


class DummyItem(pytest.Item):
    def __init__(self, pytest_file, parent):
        super(DummyItem, self).__init__(pytest_file.name, parent)
        self.pytest_file = pytest_file

    def runtest(self):
        assert self.pytest_file.fspath.read() == 'I am doc.\n'


class Sybil(object):

    def pytest(self, parent, path):
        if path.ext == ".rst":
            return DummyFile(path, parent)


pytest_collect_file = Sybil().pytest
