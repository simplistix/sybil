import re
import textwrap

from sybil import Region

CODEBLOCK_START = re.compile(
    r'^\.\.\s*(invisible-)?code(-block)?::?\s*python\b'
    r'(?:\s*\:[\w-]+\:.*\n)*'
    r'(?:\s*\n)*',
    re.MULTILINE)
CODEBLOCK_END = re.compile(r'(\n\Z|\n(?=\S))')
CODEBLOCK_INITIAL_WHITESPACE = re.compile('\s*')


def evaluate_code_block(code, namespace):
    exec(code, namespace)
    # exec adds __builtins__, we don't want it:
    del namespace['__builtins__']


def find_region_sources(document, start_pattern, end_pattern):
    for start_match in re.finditer(start_pattern, document.text):
        source_start = start_match.end()
        end_match = end_pattern.search(document.text, source_start)
        source_end = end_match.start()
        source = document.text[source_start:source_end]
        yield start_match, end_match, source


class CodeBlockParser(object):

    def __init__(self, future_imports=()):
        self.future_imports = future_imports

    def __call__(self, document):
        for start_match, end_match, source in find_region_sources(
            document, CODEBLOCK_START, CODEBLOCK_END
        ):
            source = textwrap.dedent(source)
            # There must be a nicer way to get code.co_firstlineno
            # to be correct...
            line_count = document.text.count('\n', 0, start_match.end())
            if self.future_imports:
                line_count -= 1
                source = 'from __future__ import {}\n{}'.format(
                    ', '.join(self.future_imports), source
                )
            line_prefix = '\n' * line_count
            source = line_prefix + source
            code = compile(source, document.path, 'exec', dont_inherit=True)
            yield Region(
                start_match.start(),
                end_match.end(),
                code,
                evaluate_code_block
            )
