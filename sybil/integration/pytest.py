from __future__ import absolute_import

import pytest
from _pytest._code.code import TerminalRepr

from ..example import SybilFailure


class SybilFailureRepr(TerminalRepr):

    def __init__(self, item, message):
        self.item = item
        self.message = message

    def toterminal(self, tw):
        tw.line()
        for line in self.message.splitlines():
            tw.line(line)
        tw.line()
        tw.write(self.item.parent.name, bold=True, red=True)
        tw.line(":%s: SybilFailure" % self.item.example.line)


class SybilItem(pytest.Item):

    def __init__(self, parent, example):
        name = 'line:{},column:{}'.format(example.line, example.column)
        super(SybilItem, self).__init__(name, parent)
        self.example = example

    def reportinfo(self):
        info = '%s line=%i column=%i' % (
            self.fspath.basename, self.example.line, self.example.column
        )
        return self.example.path, self.example.line, info

    def runtest(self):
        self.example.evaluate()

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, SybilFailure):
            return SybilFailureRepr(self, str(excinfo.value))
        return super(SybilItem, self).repr_failure(excinfo)


class SybilFile(pytest.File):

    def __init__(self, path, parent, sybil):
        super(SybilFile, self).__init__(path, parent)
        self.sybil = sybil

    def collect(self):
        for example in self.sybil.parse(self.fspath.strpath):
            yield SybilItem(self, example)


def pytest_integration(sybil):

    def pytest_collect_file(parent, path):
        if path.fnmatch(sybil.pattern):
            return SybilFile(path, parent, sybil)

    return pytest_collect_file
