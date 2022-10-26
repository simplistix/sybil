from __future__ import print_function

from sybil import Sybil
from sybil.parsers.myst import (
    DocTestDirectiveParser,
    PythonCodeBlockParser,
    SkipParser,
)
from sybil.parsers.rest import DocTestDirectiveParser as ReSTDocTestDirectiveParser

pytest_collect_file = Sybil(
    parsers=[
        DocTestDirectiveParser(),
        PythonCodeBlockParser(),
        ReSTDocTestDirectiveParser(),
        SkipParser(),
    ],
    pattern='*.md',
).pytest()
