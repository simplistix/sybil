import re
import textwrap

from sybil import Region

SKIP = re.compile(r'^[ \t]*\.\.\s*skip:\s*(\w+)', re.MULTILINE)


class Skip(object):

    def __init__(self, original_evaluator):
        self.original_evaluator = original_evaluator
        self.restore_next = False

    def __call__(self, example):
        if example.parsed == 'next':
            self.restore_next = True
        elif self.restore_next or example.parsed == 'end':
            example.document.evaluator = self.original_evaluator


def evaluate_skip(example):
    evaluator = example.document.evaluator
    if not isinstance(evaluator, Skip):
        example.document.evaluator = evaluator = Skip(evaluator)
    evaluator(example)


def skip(document):
    """
    A parser function to be included when your documentation makes use of
    :ref:`skipping <skip-parser>` examples in a document.
    """
    for match in re.finditer(SKIP, document.text):
        yield Region(match.start(), match.end(), match.group(1), evaluate_skip)
