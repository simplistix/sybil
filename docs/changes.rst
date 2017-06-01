Changes
=======

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
