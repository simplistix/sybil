import pytest


def pytest_collect_file(parent, path):
    if path.ext == ".rst":
        return DummyFile(path, parent)


class DummyFile(pytest.File):
    def collect(self):
        yield DummyItem(self, self)


class DummyItem(pytest.Item):
    def __init__(self, pytest_file, parent):
        super(DummyItem, self).__init__(pytest_file.name, parent)
        self.pytest_file = pytest_file

    def runtest(self):
        assert self.pytest_file.fspath.read() == 'I am doc.\n'
