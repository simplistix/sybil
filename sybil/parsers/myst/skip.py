import re

from sybil.parsers.abstract import AbstractSkipParser


class SkipParser(AbstractSkipParser):
    """
    A :any:`Parser` for :ref:`skip <myst-skip-parser>` instructions.
    """

    pattern = re.compile(r'^[ \t]*;\s*skip:\s*(\w+)(?:\s+if(.+)$)?', re.MULTILINE)
