from doctest import ELLIPSIS

from sybil import Sybil, DocTestParser, CodeBlockParser
from sybil.parsers.doctest import FIX_BYTE_UNICODE_REPR

pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS|FIX_BYTE_UNICODE_REPR),
        CodeBlockParser(future_imports=['print_function']),
    ],
    pattern='*.rst',
).pytest()
