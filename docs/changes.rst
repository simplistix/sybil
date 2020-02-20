Changes
=======

1.2.2 (20 Feb 2020)
-------------------

- Improvements to :attr:`~sybil.parsers.doctest.FIX_BYTE_UNICODE_REPR`
  for multiple strings on a single line.

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

  __ https://circleci.com/gh/cjw296/sybil
  __ https://github.com/cjw296/carthorse

- Add warning about the limitations of
  :attr:`~sybil.parsers.doctest.FIX_BYTE_UNICODE_REPR`.

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
  :class:`~sybil.parsers.doctest.DocTestParser`. Previously, tabs were
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

- Fix another bug in :class:`~sybil.parsers.codeblock.CodeBlockParser` where
  a :rst:dir:`code-block` followed by a less-indented block would be
  incorrectly indented, resulting in a :class:`SyntaxError`.

1.0.3 (2 June 2017)
-------------------

- Fix bug in :func:`~sybil.parsers.codeblock.CodeBlockParser` where it
  would incorrectly parse indented code blocks.

1.0.2 (1 June 2017)
-------------------

- Fix bug in :func:`~sybil.parsers.codeblock.CodeBlockParser` where it
  would not find indented code blocks.

1.0.1 (30 May 2017)
-------------------

- Fix bug where unicode and byte literals weren't corrected in doctest
  tracebacks, even when :attr:`sybil.parsers.doctest.FIX_BYTE_UNICODE_REPR`
  was specified.

1.0.0 (26 May 2017)
-------------------

- Initial release
