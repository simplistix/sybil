import sys
from os.path import join, dirname, abspath
from pathlib import Path
from typing import Sequence, Callable, Collection, Iterable

from .document import Document
from .typing import Parser


class Sybil:
    """
    An object to provide test runner integration for discovering examples
    in documentation and ensuring they are correct.
    
    :param parsers: 
      A sequence of callables. See :doc:`parsers`.
      
    :param path:
      The path in which source files are found, relative
      to the path of the Python source file in which this class is instantiated.
      Absolute paths can also be passed.

      .. note::

        This is ignored when using the :ref:`pytest integration <pytest_integration>`.
      
    :param pattern:
      An optional :func:`pattern <fnmatch.fnmatch>` used to match source
      files that will be parsed for examples.
      
    :param patterns:
      An optional sequence of :func:`patterns <fnmatch.fnmatch>` used to match source
      paths that will be parsed for examples.

    :param exclude:
      An optional :func:`patterns <fnmatch.fnmatch>` for source file names
      that will excluded when looking for examples.

    :param excludes:
      An optional  sequence of :func:`patterns <fnmatch.fnmatch>` for source paths
      that will be excluded when looking for examples.

    :param filenames:
      An optional collection of file names that, if found anywhere within the
      root ``path`` or its sub-directories, will be parsed for examples.

    :param setup:
      An optional callable that will be called once before any examples from
      a :class:`~sybil.document.Document` are evaluated. If provided, it is
      called with the document's :attr:`~sybil.document.Document.namespace`.
      
    :param teardown:
      An optional callable that will be called after all the examples from
      a :class:`~sybil.document.Document` have been evaluated. If provided, 
      it is called with the document's :attr:`~sybil.document.Document.namespace`.
      
    :param fixtures:
      An optional sequence of strings specifying the names of fixtures to 
      be requested when using the  :ref:`pytest integration <pytest_integration>`.
      The fixtures will be inserted into the document's :attr:`~sybil.document.Document.namespace`
      before any examples for that document are evaluated.
      All scopes of fixture are supported.

    :param encoding:
      An optional string specifying the encoding to be used when decoding documentation
      source files.
    """
    def __init__(
        self,
        parsers: Sequence[Parser],
        pattern: str = None,
        patterns: Sequence[str] = (),
        exclude: str = None,
        excludes: Sequence[str] = (),
        filenames: Collection[str] = (),
        path: str = '.',
        setup: Callable[[dict], None] = None,
        teardown: Callable[[dict], None] = None,
        fixtures: Sequence[str] = (),
        encoding: str = 'utf-8',
    ):
        self.parsers: Sequence[Parser] = parsers
        calling_filename = sys._getframe(1).f_globals.get('__file__')
        if calling_filename:
            start_path = join(dirname(calling_filename), path)
        else:
            start_path = path
        self.path: str = abspath(start_path)
        self.patterns = list(patterns)
        if pattern:
            self.patterns.append(pattern)
        self.excludes = list(excludes)
        if exclude:
            self.excludes.append(exclude)
        self.filenames = filenames
        self.setup: Callable[[dict], None] = setup
        self.teardown: Callable[[dict], None] = teardown
        self.fixtures: Sequence[str] = fixtures
        self.encoding: str = encoding

    def should_parse(self, path: Path) -> bool:
        root = Path(self.path)
        try:
            path = path.relative_to(root)
        except ValueError:
            return False

        include = False
        if any(path.match(p) for p in self.patterns):
            include = True
        if path.name in self.filenames:
            include = True
        if not include:
            return False

        if any(path.match(e) for e in self.excludes):
            return False
        return True

    def parse(self, path: str) -> Document:
        return Document.parse(path, *self.parsers, encoding=self.encoding)

    def pytest(self):
        """
        The helper method for when you use :ref:`pytest_integration`.
        """
        from .integration.pytest import pytest_integration
        return pytest_integration(self)

    def unittest(self):
        """
        The helper method for when you use :ref:`unitttest_integration`.
        """
        from .integration.unittest import unittest_integration
        return unittest_integration(self)

