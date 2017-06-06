Changes
=======

1.0.5 (6 June 2017)
-------------------

- Fix ordering issue that would cause some tests to fail when run on systems
  using tmpfs.

1.0.4 (5 June 2017)
-------------------

- Fix another bug in :func:`~sybil.parsers.codeblock.CodeBlockParser` where
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
  tracebacks, event when :attr:`sybil.parsers.doctest.FIX_BYTE_UNICODE_REPR`
  was specified.

1.0.0 (26 May 2017)
-------------------

- Initial release
