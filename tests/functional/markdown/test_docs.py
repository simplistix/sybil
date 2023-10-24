from __future__ import print_function

from sybil import Sybil
from sybil.parsers.markdown import (
    PythonCodeBlockParser,
    SkipParser,
)

load_tests = Sybil(
    parsers=[
        PythonCodeBlockParser(),
        SkipParser(),
    ],
    pattern='*.md',
).unittest()
