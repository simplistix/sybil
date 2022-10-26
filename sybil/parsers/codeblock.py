import __future__
import re
import textwrap
from typing import Iterable

from sybil import Region, Document, Example
from sybil.evaluators.python import pad, PythonEvaluator
from sybil.typing import Evaluator

CODEBLOCK_START = re.compile(
    r'^(?P<indent>[ \t]*)\.\.\s*(invisible-)?code(-block)?::?\s*(?P<language>[\w-]+)\b'
    r'(?:\s*\:[\w-]+\:.*\n)*'
    r'(?:\s*\n)*',
    re.MULTILINE)


class CodeBlockParser:
    """
    A class to instantiate and include when your documentation makes use of
    :ref:`codeblock-parser` examples.

    :param language:
        The language that this parser should look for.

    :param evaluator:
        The evaluator to use for evaluating code blocks in the specified language.
        You can also override the :meth:`evaluate` below.
    """

    language: str

    def __init__(self, language: str = None, evaluator: Evaluator = None):
        if language is not None:
            self.language = language
        assert self.language, 'language must be specified!'
        if evaluator is not None:
            self.evaluate = evaluator

    pad = staticmethod(pad)

    def evaluate(self, example: Example):
        raise NotImplementedError

    def __call__(self, document: Document) -> Iterable[Region]:
        for start_match in re.finditer(CODEBLOCK_START, document.text):
            if start_match.group('language') != self.language:
                continue
            source_start = start_match.end()
            indent = str(len(start_match.group('indent')))
            end_pattern = re.compile(r'(\n\Z|\n[ \t]{0,'+indent+'}(?=\\S))')
            end_match = end_pattern.search(document.text, source_start)
            source_end = end_match.start()
            source = textwrap.dedent(document.text[source_start:source_end])
            yield Region(
                start_match.start(),
                source_end,
                source,
                self.evaluate
            )


class PythonCodeBlockParser(CodeBlockParser):
    """
    A class to instantiate and include when your documentation makes use of
    Python :ref:`codeblock-parser` examples.
     
    :param future_imports: 
        An optional list of strings that will be turned into
        ``from __future__ import ...`` statements and prepended to the code
        in each of the examples found by this parser.
    """

    def __init__(self, future_imports=()):
        super().__init__(language='python', evaluator=PythonEvaluator(future_imports))
