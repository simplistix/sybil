from __future__ import print_function

from sybil import Sybil
from sybil.parsers.markdown import (
    PythonCodeBlockParser,
    SkipParser,
)

pytest_collect_file = Sybil(
    parsers=[
        PythonCodeBlockParser(),
        SkipParser(),
    ],
    pattern='*.md',
).pytest()
