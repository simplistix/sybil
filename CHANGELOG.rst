Changes
=======

9.1.0 (18 Feb 2025)
-------------------

- The various "skip" parsers can now be subclassed to specify a different directive name.

- Clearer error message when a "skip" directive is encountered with missing parameters.

Thanks to Adam Dangoor for the work on these!

9.0.0 (12 Nov 2024)
-------------------

- Retire ``Document.find_region_sources()`` in favour of using a
  :class:`~sybil.parsers.abstract.lexers.BlockLexer`.
  See the :ref:`updated example <parser-from-scratch>`.

- Better error messages when lexing fails to find the end of a block.

- Improved documentation.

8.0.1 (30 Oct 2024)
-------------------

- Better error message when skip arguments are malformed.

- Remove unused constant that caused problems with development releases of pytest.

8.0.0 (20 Sep 2024)
-------------------

- Drop Python 3.8 support.

- Internal code tidying.

Thanks to Adam Dangoor for the work on these!

7.1.1 (16 Sep 2024)
-------------------

- Fix bug that broke docstring collection where a method had an :any:`ellipsis <Ellipsis>` in
  place of the docstring.

7.1.0 (16 Sep 2024)
-------------------

- Introduce a ``pytest`` extra, such that you can install Sybil in a way that ensures
  compatible versions of Sybil and pytest are used.

- Fix a :class:`DeprecationWarning` on Python 3.13.

Thanks to Adam Dangoor for this fix.

7.0.0 (12 Sep 2024)
-------------------

- Drop Python 3.7 support.

- Drop support for pytest versions less than 8.

- :class:`Sybil` now takes a name which is used in any test identifiers it produces.

- Add support for :rst:dir:`code` and :rst:dir:`sourcecode` directives in both ReST and MyST.

- Fix bug in the pytest integration that prevented multiple :class:`Sybil` instances from
  parsing the same file.

- Fix bug where escaped quotes were not correctly unescaped in regions extracted from docstrings.

- Restructure usage documentation, splitting out :doc:`integration` and :doc:`parsers`
  documents and introducing a :doc:`concepts` glossary.

6.1.1 (9 May 2024)
------------------

- Fix lexing of indented blocks where embedded blank lines would be erroneously removed.

6.1.0 (22 Apr 2024)
-------------------

- Add support for lexing nested fenced codeblocks in markdown.

- Add support for tilde-delimited codeblocks in markdown.

- Fix bug with the end offset of codeblocks in markdown.

6.0.3 (31 Jan 2024)
-------------------

- Support pytest 8 and above, due to yet another breaking change in an API Sybil relies on.


Thanks to Adam Dangoor for the fix.

6.0.2 (23 Nov 2023)
-------------------

- Remove use of deprecated ``py.path.local``.

6.0.1 (22 Nov 2023)
-------------------

- Fix lexing of ReST directives and directives-in-comments where the directives
  were not separated by at least one newline.

6.0.0 (21 Nov 2023)
-------------------

- The public interface is now fully typed and checked with ``mypy``.

- Official support for Python 3.12 with Python 3.7 now being the minimum
  supported version.

- :doc:`Markdown <markdown>` is now supported separately to
  :doc:`MyST <myst>`.

- :any:`ReST <sybil.parsers.rest.lexers.DirectiveLexer>` and
  :any:`MyST <sybil.parsers.myst.lexers.DirectiveLexer>` directives
  now have their options extracted as part of the lexing process.

- Added support for MyST single-line html-style comment directives.

- Fixed parsing of MyST directive options with no leading whitespace.

- Fixed parsing of Markdown and MyST fenced codeblocks at the end of documents with no
  trailing newline.

- Rework document evaluators to be more flexible and structured.

- :ref:`skip <skip-parser>` has been reworked to check validity of operations
  and allow a reason to be provided for an unconditional skip so it can be
  highlighted as a skipped test in test runner output. The skip parsers
  are also now lexer-based.

- Make :attr:`Region.evaluator` optional, removing the need for the separate
  ``LexedRegion`` class.

Huge thanks to Adam Dangoor for all his work on typing!

5.0.3 (14 Jul 2023)
-------------------

- Fix bug in traceback trimming on the latest release of pytest.

5.0.2 (19 May 2023)
-------------------

- Fixed bug in the :func:`repr` of ``LexedRegion`` instances where a lexeme was ``None``.

- Fixed lexing of ReST directives, such as :rst:dir:`code-block`, where they occurred
  at the end of a docstring.

- Ensure the :class:`~sybil.Document.namespace` in which doctests are evaluated always has a
  ``__name__``. This is required by an implementation detail of :any:`typing.runtime_checkable`.

5.0.1 (9 May 2023)
------------------

- Fix a bug that prevent r-prefixed docstrings from being correctly parsed from ``.py`` files.

5.0.0 (26 Mar 2023)
-------------------

- By default, on Python 3.8 and above, when parsing ``.py`` files, only examples in docstrings
  will be parsed.

- The :attr:`~sybil.Document.namespace` can now be cleared in both
  :ref:`ReST <clear-namespace>` and
  :ref:`MyST <myst-clear-namespace>`.

- Support for Python 3.6 has been dropped.

- Support for pytest versions earlier than 7.1 has been dropped.

4.0.1 (8 Feb 2023)
------------------

- Switch :func:`sybil.parsers.myst.SkipParser` to use the correct comment character.

- Note that the :external+sphinx:doc:`doctest extension <usage/extensions/doctest>` needs to be
  enabled to render :rst:dir:`doctest` directives.

- Warn about :ref:`ReST <doctest-parser>` and :ref:`MyST <myst-doctest-parser>` doctest parsers
  and overlapping blocks.

4.0.0 (25 Dec 2022)
-------------------

- Restructure to support lexing source languages such as ReST and MyST
  while testing examples in target languages such as Python, doctest and bash.

- Add support for :doc:`MyST examples <myst>`.

- Include a :ref:`plan for migrating <migrating-from-sphinx.ext.doctest>`
  from ``sphinx.ext.doctest``.

3.0.1 (25 Feb 2022)
-------------------

- Continue with the ever shifting sands of pytest APIs, this time appeasing
  warnings from pytest 7 that when fixed break compatibility with pytest 6.

3.0.0 (26 Oct 2021)
-------------------

- Require pytest 6.2.0.

- Drop Python 2 support.

- Add support for Python 3.10

- Remove the ``encoding`` parameter to :class:`~sybil.parsers.rest.DocTestParser`
  as it is no longer used.

- :class:`~sybil.parsers.rest.CodeBlockParser` has been renamed to
  :class:`~sybil.parsers.rest.PythonCodeBlockParser`, see the
  :ref:`codeblock-parser` documentation for details.

- Support has been added to check examples in Python source code in addition to
  documentation source files.

- ``FIX_BYTE_UNICODE_REPR`` has been removed as it should no
  longer be needed.

Thanks to Stefan Behnel for his work on :ref:`codeblock-parser` parsing!

2.0.1 (29 Nov 2020)
-------------------

- Make :class:`~sybil.parsers.rest.DocTestParser` more permissive with respect
  to tabs in documents. Tabs that aren't in the doctest block not longer cause
  parsing of the document to fail.

2.0.0 (17 Nov 2020)
-------------------

- Drop support for nose.

- Handle encoded data returned by doctest execution on Python 2.

1.4.0 (5 Aug 2020)
------------------

- Support nested directories of source files rather than just one directory.

- Support multiple patterns of files to include.

1.3.1 (29 Jul 2020)
-------------------

- Support pytest 6.

1.3.0 (28 Mar 2020)
-------------------

- Treat all documentation source files as being ``utf-8`` encoded. This can be overridden
  by passing an encoding when instantiating a :class:`~sybil.Sybil`.

1.2.2 (20 Feb 2020)
-------------------

- Improvements to ``FIX_BYTE_UNICODE_REPR`` for multiple strings on a single line.

- Better handling of files with Windows line endings on Linux under Python 2.

1.2.1 (21 Jan 2020)
-------------------

- Fixes for pytest 3.1.0.

1.2.0 (28 Apr 2019)
-------------------

- Only compile code in :ref:`codeblocks <codeblock-parser>` at evaluation time,
  giving :ref:`skip <skip-parser>` a chance to skip code blocks that won't
  compile on a particular version of Python.

1.1.0 (25 Apr 2019)
-------------------

- Move to CircleCI__ and Carthorse__.

  __ https://circleci.com/gh/simplistix/sybil
  __ https://github.com/cjw296/carthorse

- Add warning about the limitations of ``FIX_BYTE_UNICODE_REPR``.

- Support explicit filenames to include and patterns to exclude
  when instantiating a :class:`~sybil.Sybil`.

- Add the :ref:`skip <skip-parser>` parser.

1.0.9 (1 Aug 2018)
------------------

- Fix for pytest 3.7+.

1.0.8 (6 Apr 2018)
------------------

- Changes only to unit tests to support fixes in the latest release of pytest.

1.0.7 (25 January 2018)
-----------------------

- Literal tabs may no longer be included in text that is parsed by the
  :class:`~sybil.parsers.rest.DocTestParser`. Previously, tabs were
  expanded which could cause unpleasant problems.

1.0.6 (30 November 2017)
------------------------

- Fix compatibility with pytest 3.3+.

Thanks to Bruno Oliveira for this fix!

1.0.5 (6 June 2017)
-------------------

- Fix ordering issue that would cause some tests to fail when run on systems
  using tmpfs.

1.0.4 (5 June 2017)
-------------------

- Fix another bug in :class:`~sybil.parsers.rest.CodeBlockParser` where
  a :rst:dir:`code-block` followed by a less-indented block would be
  incorrectly indented, resulting in a :class:`SyntaxError`.

1.0.3 (2 June 2017)
-------------------

- Fix bug in :class:`~sybil.parsers.rest.CodeBlockParser` where it
  would incorrectly parse indented code blocks.

1.0.2 (1 June 2017)
-------------------

- Fix bug in :class:`~sybil.parsers.rest.CodeBlockParser` where it
  would not find indented code blocks.

1.0.1 (30 May 2017)
-------------------

- Fix bug where unicode and byte literals weren't corrected in doctest
  tracebacks, even when ``FIX_BYTE_UNICODE_REPR``
  was specified.

1.0.0 (26 May 2017)
-------------------

- Initial release
