from __future__ import absolute_import

from inspect import getsourcefile
from os.path import abspath

from _pytest._code.code import TerminalRepr, Traceback
from _pytest import fixtures
from _pytest.fixtures import FuncFixtureInfo
from _pytest.main import Session
from _pytest.python import Module
import py.path
import pytest

from ..example import SybilFailure
from .. import example

example_module_path = abspath(getsourcefile(example))


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

    def __init__(self, parent, sybil, example):
        name = 'line:{},column:{}'.format(example.line, example.column)
        super(SybilItem, self).__init__(name, parent)
        self.example = example
        self.request_fixtures(sybil.fixtures)

    def request_fixtures(self, names):
        # pytest fixtures dance:
        fm = self.session._fixturemanager
        closure = fm.getfixtureclosure(names, self)
        try:
            initialnames, names_closure, arg2fixturedefs = closure
        except ValueError:  # pragma: no cover
            # pytest < 3.7
            names_closure, arg2fixturedefs = closure
            fixtureinfo = FuncFixtureInfo(names, names_closure, arg2fixturedefs)
        else:
            # pyest >= 3.7
            fixtureinfo = FuncFixtureInfo(names, initialnames, names_closure, arg2fixturedefs)
        self._fixtureinfo = fixtureinfo
        self.funcargs = {}
        self._request = fixtures.FixtureRequest(self)

    def reportinfo(self):
        info = '%s line=%i column=%i' % (
            self.fspath.basename, self.example.line, self.example.column
        )
        return py.path.local(self.example.document.path), self.example.line, info

    def getparent(self, cls):
        if cls is Module:
            return self.parent
        if cls is Session:
            return self.session

    def setup(self):
        self._request._fillfixtures()
        for name, fixture in self.funcargs.items():
            self.example.namespace[name] = fixture

    def runtest(self):
        self.example.evaluate()

    def _prunetraceback(self, excinfo):
        # Messier than it could be because slicing a list subclass in
        # Python 2 returns a list, not an instance of the subclass.
        tb = excinfo.traceback.cut(path=example_module_path)
        tb = tb[1]
        if getattr(tb, '_rawentry', None) is not None:
            excinfo.traceback = Traceback(tb._rawentry, excinfo)

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, SybilFailure):
            return SybilFailureRepr(self, str(excinfo.value))
        return super(SybilItem, self).repr_failure(excinfo)


class SybilFile(pytest.File):

    def __init__(self, fspath, parent, sybil):
        super(SybilFile, self).__init__(fspath, parent)
        self.sybil = sybil

    def collect(self):
        self.document = self.sybil.parse(self.fspath.strpath)
        for example in self.document:
            try:
                from_parent = SybilItem.from_parent
            except AttributeError:
                yield SybilItem(self, self.sybil, example)
            else:
                yield from_parent(self, sybil=self.sybil, example=example)

    def setup(self):
        if self.sybil.setup:
            self.sybil.setup(self.document.namespace)

    def teardown(self):
        if self.sybil.teardown:
            self.sybil.teardown(self.document.namespace)


def pytest_integration(sybil, class_=SybilFile):

    def pytest_collect_file(parent, path):
        if sybil.should_test_path(path):
            try:
                from_parent = class_.from_parent
            except AttributeError:
                return class_(path, parent, sybil)
            else:
                return from_parent(parent, fspath=path, sybil=sybil)

    return pytest_collect_file
