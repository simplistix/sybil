from doctest import ELLIPSIS
from sybil import Sybil
from sybil.parsers.rest import (
    CaptureParser,
    DocTestParser,
    PythonCodeBlockParser,
    SkipParser,
)

pytest_collect_file = Sybil(
    parsers=[
        CaptureParser(),
        DocTestParser(optionflags=ELLIPSIS),
        PythonCodeBlockParser(),
        SkipParser(),
    ],
    patterns=['*.rst', '*.py'],
).pytest()
