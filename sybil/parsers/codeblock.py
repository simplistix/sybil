import re
import textwrap

from sybil import Region

CODEBLOCK_START = re.compile(
    r'(^\.\.\s*(invisible-)?code(-block)?::?\s*python\b(?:\s*\:[\w-]+\:.*\n)*)',
    re.MULTILINE)
CODEBLOCK_END = re.compile(r'(\n\Z|\n(?=\S))')


def evaluate_code_block(code, namespace):
    exec(code, namespace)
    # exec adds __builtins__, we don't want it:
    del namespace['__builtins__']


class CodeBlockParser(object):

    def __init__(self):
        pass

    def __call__(self, document):
        for start, end, source in document.find_region_sources(
            CODEBLOCK_START, CODEBLOCK_END
        ):
            source = textwrap.dedent(source)
            code = compile(source, document.path, 'exec', dont_inherit=True)
            yield Region(start, end, code, evaluate_code_block)
