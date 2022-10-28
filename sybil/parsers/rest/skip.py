import re

from sybil.parsers.abstract import AbstractSkipParser


class SkipParser(AbstractSkipParser):

    pattern = re.compile(r'^[ \t]*\.\.\s*skip:\s*(\w+)(?:\s+if(.+)$)?', re.MULTILINE)
