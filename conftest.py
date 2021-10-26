from doctest import ELLIPSIS
from sybil import Sybil
from sybil.parsers.capture import parse_captures
from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.skip import skip

pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS),
        PythonCodeBlockParser(),
        parse_captures,
        skip,
    ],
    patterns=['*.rst', '*.py'],
).pytest()
