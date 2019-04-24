import re
import textwrap

from sybil import Region

CODEBLOCK_START = re.compile(
    r'^(?P<indent>[ \t]*)\.\.\s*(invisible-)?code(-block)?::?\s*python\b'
    r'(?:\s*\:[\w-]+\:.*\n)*'
    r'(?:\s*\n)*',
    re.MULTILINE)


def evaluate_code_block(example):
    exec(example.parsed, example.namespace)
    # exec adds __builtins__, we don't want it:
    del example.namespace['__builtins__']


class CodeBlockParser(object):
    """
    A class to instantiate and include when your documentation makes use of
    :ref:`codeblock-parser` examples.
     
    :param future_imports: 
        An optional list of strings that will be turned into
        ``from __future__ import ...`` statements and prepended to the code
        in each of the examples found by this parser.
    """

    def __init__(self, future_imports=()):
        self.future_imports = future_imports

    def __call__(self, document):
        for start_match in re.finditer(CODEBLOCK_START, document.text):
            source_start = start_match.end()
            indent = str(len(start_match.group('indent')))
            end_pattern = re.compile(r'(\n\Z|\n[ \t]{0,'+indent+'}(?=\S))')
            end_match = end_pattern.search(document.text, source_start)
            source_end = end_match.start()
            source = textwrap.dedent(document.text[source_start:source_end])
            # There must be a nicer way to get code.co_firstlineno
            # to be correct...
            line_count = document.text.count('\n', 0, source_start)
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
                source_end,
                code,
                evaluate_code_block
            )
