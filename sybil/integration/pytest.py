from __future__ import absolute_import

from inspect import getsourcefile
from os.path import abspath
from pathlib import Path
from typing import Union, TYPE_CHECKING

from _pytest._code.code import TerminalRepr, Traceback, ExceptionInfo
from _pytest import fixtures
from _pytest.fixtures import FuncFixtureInfo
from _pytest.main import Session
from _pytest.nodes import Collector
from _pytest.python import Module
import py.path
import pytest

from ..example import SybilFailure
from .. import example

if TYPE_CHECKING:
    from ..sybil import Sybil

PYTEST_VERSION = tuple(int(i) for i in pytest.__version__.split('.'))

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
        initialnames, names_closure, arg2fixturedefs = closure
        fixtureinfo = FuncFixtureInfo(names, initialnames, names_closure, arg2fixturedefs)
        self._fixtureinfo = fixtureinfo
        self.funcargs = {}
        self._request = fixtures.FixtureRequest(self, _ispytest=True)

    def reportinfo(self):
        info = '%s line=%i column=%i' % (
            self.fspath.basename, self.example.line, self.example.column
        )
        return py.path.local(self.example.path), self.example.line, info

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
        tb = excinfo.traceback.cut(path=example_module_path)
        tb = tb[1]
        if getattr(tb, '_rawentry', None) is not None:
            excinfo.traceback = Traceback(tb._rawentry, excinfo)

    def repr_failure(
        self,
        excinfo: ExceptionInfo[BaseException],
        style = None,
    ) -> Union[str, TerminalRepr]:
        if isinstance(excinfo.value, SybilFailure):
            return SybilFailureRepr(self, str(excinfo.value))
        return super().repr_failure(excinfo, style)


class SybilFile(pytest.File):

    def __init__(self, *, sybil: 'Sybil', **kwargs):
        super(SybilFile, self).__init__(**kwargs)
        self.sybil: 'Sybil' = sybil

    def collect(self):
        self.document = self.sybil.parse(Path(self.fspath.strpath))
        for example in self.document:
            yield SybilItem.from_parent(self, sybil=self.sybil, example=example)

    def setup(self):
        if self.sybil.setup:
            self.sybil.setup(self.document.namespace)

    def teardown(self):
        if self.sybil.teardown:
            self.sybil.teardown(self.document.namespace)


def pytest_integration(*sybils: 'Sybil'):

    def pytest_collect_file(path: py.path.local, parent: Collector):
        fspath = path
        path = Path(fspath.strpath)
        for sybil in sybils:
            if sybil.should_parse(path):
                if PYTEST_VERSION[0] >= 7:
                    return SybilFile.from_parent(parent, path=path, sybil=sybil)
                else:
                    return SybilFile.from_parent(parent, fspath=fspath, sybil=sybil)

    return pytest_collect_file
