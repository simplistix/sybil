import re
import textwrap

from sybil import Region

RE_CODEBLOCK_START = (
    r'^(?P<indent>[ \t]*)\.\.\s*(invisible-)?code(-block)?::?\s*{{BLOCKLANGUAGE}}\b'
    r'(?:\s*\:[\w-]+\:.*\n)*'
    r'(?:\s*\n)*'
)


def compile_codeblock(source, path):
    return compile(source, path, 'exec', dont_inherit=True)


def evaluate_code_block(example):
    code = compile_codeblock(example.parsed, example.document.path)
    exec(code, example.namespace)
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

    Subclasses can override the language handled by this parser as follows.

    - Overwrite the `LANGUAGE` attribute with the name of the language.

    - Implement the `evaluation_function()` method to return an evaluation
      function for that language.  The function will receive a
      :class:`~sybil.example.Example` object as only argument, containing the
      code that was parsed from the code block section.
    """

    LANGUAGE = 'python'

    def __init__(self, future_imports=()):
        self.future_imports = future_imports
        self.block_start = re.compile(
            RE_CODEBLOCK_START.replace('{{BLOCKLANGUAGE}}', self.LANGUAGE),
            re.MULTILINE,
        )

    @staticmethod
    def evaluation_function():
        return evaluate_code_block

    def __call__(self, document):
        evaluator_function = self.evaluation_function()

        for start_match in re.finditer(self.block_start, document.text):
            source_start = start_match.end()
            indent = str(len(start_match.group('indent')))
            end_pattern = re.compile(r'(\n\Z|\n[ \t]{0,'+indent+'}(?=\\S))')
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
            yield Region(
                start_match.start(),
                source_end,
                source,
                evaluator_function,
            )
