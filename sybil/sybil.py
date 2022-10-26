import sys
from pathlib import Path
from typing import Sequence, Callable, Collection, Mapping, Optional, Type, List

from .document import Document, PythonDocument
from .typing import Parser


DEFAULT_DOCUMENT_TYPES = {
    None: Document,
    '.py': PythonDocument,
}


class Sybil:
    """
    An object to provide test runner integration for discovering examples
    in documentation and ensuring they are correct.
    
    :param parsers: 
      A sequence of callables. See :ref:`parsers`.
      
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
      An optional :func:`pattern <fnmatch.fnmatch>` for source file names
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
      called with the document's :attr:`~sybil.Document.namespace`.
      
    :param teardown:
      An optional callable that will be called after all the examples from
      a :class:`~sybil.document.Document` have been evaluated. If provided, 
      it is called with the document's :attr:`~sybil.Document.namespace`.
      
    :param fixtures:
      An optional sequence of strings specifying the names of fixtures to 
      be requested when using the  :ref:`pytest integration <pytest_integration>`.
      The fixtures will be inserted into the document's :attr:`~sybil.Document.namespace`
      before any examples for that document are evaluated.
      All scopes of fixture are supported.

    :param encoding:
      An optional string specifying the encoding to be used when decoding documentation
      source files.

    :param document_types:
      A mapping of file extension to :class:`Document` subclass such that custom evaluation
      can be performed per document type.
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
        document_types: Mapping[Optional[str], Type[Document]] = None
    ):

        self.parsers: Sequence[Parser] = parsers
        calling_filename = sys._getframe(1).f_globals.get('__file__')
        if calling_filename:
            start_path = Path(calling_filename).parent / path
        else:
            start_path = Path(path)
        self.path: Path = start_path.absolute()
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
        self.document_types = DEFAULT_DOCUMENT_TYPES.copy()
        if document_types:
            self.document_types.update(document_types)
        self.default_document_type: Type[Document] = self.document_types[None]

    def __add__(self, other: 'Sybil'):
        """
        :class:`Sybil` instances can be concatenated into a :class:`~sybil.sybil.SybilCollection`.
        """
        assert isinstance(other, Sybil)
        return SybilCollection((self, other))

    def should_parse(self, path: Path) -> bool:
        try:
            path = path.relative_to(self.path)
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

    def parse(self, path: Path) -> Document:
        type_ = self.document_types.get(path.suffix, self.default_document_type)
        return type_.parse(str(path), *self.parsers, encoding=self.encoding)

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


class SybilCollection(list):
    """
    When :class:`Sybil` instances are concatenated, the collection returned can
    be used in the same way as a single :class:`Sybil`.

    This allows multiple configurations to be used in a single test run.
    """

    def pytest(self):
        """
        The helper method for when you use :ref:`pytest_integration`.
        """
        from .integration.pytest import pytest_integration
        return pytest_integration(*self)

    def unittest(self):
        """
        The helper method for when you use :ref:`unitttest_integration`.
        """
        from .integration.unittest import unittest_integration
        return unittest_integration(*self)
