from __future__ import absolute_import

import os
from collections.abc import Callable, Sequence
from inspect import getsourcefile
from os.path import abspath
from pathlib import Path
from typing import Union, Tuple, Optional, List

import pytest
from pytest import Collector, ExceptionInfo, Module, Session
from _pytest import fixtures
from _pytest._code.code import TerminalRepr, Traceback
from _pytest._io import TerminalWriter
from _pytest.fixtures import FuncFixtureInfo

from sybil import example as example_module, Sybil, Document
from sybil.example import Example
from sybil.example import SybilFailure

PYTEST_VERSION = tuple(int(i) for i in pytest.__version__.split('.'))

example_module_path = abspath(getsourcefile(example_module))


class SybilFailureRepr(TerminalRepr):

    def __init__(self, item: 'SybilItem', message: str) -> None:
        self.item = item
        self.message = message

    def toterminal(self, tw: TerminalWriter) -> None:
        tw.line()
        for line in self.message.splitlines():
            tw.line(line)
        tw.line()
        tw.write(self.item.parent.name, bold=True, red=True)
        tw.line(":%s: SybilFailure" % self.item.example.line)


class SybilItem(pytest.Item):

    obj = None

    def __init__(self, parent, sybil, example: Example) -> None:
        super(SybilItem, self).__init__(sybil.identify(example), parent)
        self.example = example
        self.request_fixtures(sybil.fixtures)

    def request_fixtures(self, names):
        # pytest fixtures dance:
        fm = self.session._fixturemanager
        closure = fm.getfixtureclosure(initialnames=names, parentnode=self, ignore_args=set())
        names_closure, arg2fixturedefs = closure
        fixtureinfo = FuncFixtureInfo(argnames=names, initialnames=names, names_closure=names_closure, name2fixturedefs=arg2fixturedefs)
        self._fixtureinfo = fixtureinfo
        self.funcargs = {}
        self._request = fixtures.TopRequest(pyfuncitem=self, _ispytest=True)
        self.fixturenames = names_closure

    def reportinfo(self) -> Tuple[Union["os.PathLike[str]", str], Optional[int], str]:
        info = '%s line=%i column=%i' % (
            self.path.name, self.example.line, self.example.column
        )
        return self.example.path, self.example.line, info

    def getparent(self, cls):
        if cls is Module:
            return self.parent
        if cls is Session:
            return self.session

    def setup(self) -> None:
        self._request._fillfixtures()
        for name, fixture in self.funcargs.items():
            self.example.namespace[name] = fixture

    def runtest(self) -> None:
        self.example.evaluate()

    def _traceback_filter(self, excinfo: ExceptionInfo[BaseException]) -> Traceback:
        traceback = excinfo.traceback
        tb = traceback.cut(path=example_module_path)
        tb_entry = tb[1]
        if getattr(tb_entry, '_rawentry', None) is not None:
            traceback = Traceback(tb_entry._rawentry)
        return traceback

    def repr_failure(
        self,
        excinfo: ExceptionInfo[BaseException],
        style = None,
    ) -> Union[str, TerminalRepr]:
        if isinstance(excinfo.value, SybilFailure):
            return SybilFailureRepr(self, str(excinfo.value))
        return super().repr_failure(excinfo, style)


class SybilFile(pytest.File):

    def __init__(self, *, sybils: Sequence[Sybil], **kwargs) -> None:
        super(SybilFile, self).__init__(**kwargs)
        self.sybils: Sequence[Sybil] = sybils
        self.documents: List[Document] = []

    def collect(self):
        for sybil in self.sybils:
            document = sybil.parse(self.path)
            self.documents.append(document)
            for example in document.examples():
                yield SybilItem.from_parent(
                    self,
                    sybil=sybil,
                    example=example,
                )

    def setup(self) -> None:
        for sybil, document in zip(self.sybils, self.documents):
            if sybil.setup:
                sybil.setup(document.namespace)

    def teardown(self) -> None:
        for sybil, document in zip(self.sybils, self.documents):
            if sybil.teardown:
                sybil.teardown(document.namespace)


def pytest_integration(*sybils: Sybil) -> Callable[[Path, Collector], Optional[SybilFile]]:

    def pytest_collect_file(file_path: Path, parent: Collector) -> Optional[SybilFile]:
        active_sybils = [sybil for sybil in sybils if sybil.should_parse(file_path)]
        if active_sybils:
            return SybilFile.from_parent(parent, path=file_path, sybils=active_sybils)
        return None

    return pytest_collect_file
