"""
This is a module doc string.
"""  # This is a comment on how annoying 3.7 and earlier are!
import re
from functools import partial
from pathlib import Path
from typing import Iterable

from testfixtures import compare, ShouldRaise

from sybil import Region, Example
from sybil.document import PythonDocStringDocument, Document
from sybil.example import NotEvaluated, SybilFailure
from sybil.exceptions import LexingException
from .helpers import ast_docstrings, skip_if_37_or_older, parse, sample_path


@skip_if_37_or_older()
def test_extract_docstring():
    """
    This is a function docstring.
    """
    python_source_code = Path(__file__).read_text()
    expected = list(ast_docstrings(python_source_code))
    actual = list(PythonDocStringDocument.extract_docstrings(python_source_code))
    compare(expected, actual=[text for _, _, text in actual], show_whitespace=True)
    compare(expected, actual=[python_source_code[s:e] for s, e, _ in actual], show_whitespace=True)


@skip_if_37_or_older()
def test_all_docstrings_extracted_correctly(python_file):
    problems = []
    path, source = python_file
    expected = list(ast_docstrings(source))
    actual = list(PythonDocStringDocument.extract_docstrings(source))
    check = partial(compare, prefix=str(path), raises=False, show_whitespace=True)
    for check_result in (
        check(expected=len(expected), actual=len(actual)),
        check(expected, actual=[text for _, _, text in actual]),
        check(expected, actual=[source[s:e] for s, e, _ in actual]),
    ):
        if check_result:  # pragma: no cover - Only on failures!
            problems.append(check_result)
    if problems:  # pragma: no cover - Only on failures!
        raise AssertionError('docstrings not correctly extracted:\n\n'+'\n\n'.join(problems))


def test_evaluator_returns_non_string():

    def evaluator(example: Example) -> NotEvaluated:
        # This is a bug!
        return NotEvaluated()

    def parser(document: Document) -> Iterable[Region]:
        yield Region(0, 1, None, evaluator)

    examples, namespace = parse('sample1.txt', parser, expected=1)
    with ShouldRaise(SybilFailure(examples[0], f'NotEvaluated()')):
        examples[0].evaluate()


def test_nested_evaluators():

    def record(example: Example, evaluator_name):
        (instruction, id_, param) = example.parsed
        example.namespace['results'].append((instruction, id_, param, evaluator_name))

    def normal_evaluator(example: Example):
        record(example, 'normal')

    class InstructionEvaluator:
        def __init__(self, id_, mode):
            self.name = f'{id_}-{mode}'
            self.mode = mode
            assert hasattr(self, mode), mode

        def __call__(self, example: Example):
            (instruction, id_, param) = example.parsed
            if instruction in ('install', 'remove'):
                raise NotEvaluated()
            record(example, self.name)
            return getattr(self, self.mode)(id_)

        def install(self, example: Example):
            record(example, self.name+'-install')
            example.document.push_evaluator(self)

        def remove(self, example: Example):
            record(example, self.name + '-remove')
            example.document.pop_evaluator(self)

        def passthrough(self, id_: int):
            raise NotEvaluated()

        def all(self, id_: int):
            return ''

        def even(self, id_: int):
            if id_ % 2:
                raise NotEvaluated()

    evaluators = {}

    def parser(document: Document) -> Iterable[Region]:
        for match in re.finditer(r'(example|install|remove)-(\d+)(.+)?', document.text):
            instruction, id_, param = match.groups()
            id_ = int(id_)
            param = param.lstrip('-') if param else None
            if instruction == 'example':
                evaluator = normal_evaluator
            else:
                obj = evaluators.get(id_)
                if obj is None:
                    obj = evaluators.setdefault(id_, InstructionEvaluator(id_, param))
                evaluator = getattr(obj, instruction)
            yield Region(match.start(), match.end(), (instruction, id_, param), evaluator)

    examples, namespace = parse('nested-evaluators.txt', parser, expected=12)
    namespace['results'] = results = []
    for e in examples:
        e.evaluate()
    compare(results, expected=[
        ('example', 0, None, 'normal'),
        ('install', 1, 'passthrough', '1-passthrough-install'),
        ('example', 2, None, '1-passthrough'),
        ('example', 2, None, 'normal'),
        ('install', 3, 'all', '3-all-install'),
        ('example', 4, None, '3-all'),
        ('install', 5, 'even', '5-even-install'),
        ('example', 6, None, '5-even'),
        ('example', 7, None, '5-even'),
        ('example', 7, None, '3-all'),
        ('remove', 5, None, '5-even-remove'),
        ('example', 8, None, '3-all'),
        ('remove', 3, None, '3-all-remove'),
        ('example', 9, None, '1-passthrough'),
        ('example', 9, None, 'normal'),
    ])


def test_nested_evaluators_not_evaluated_from_region():

    def evaluator(example: Example):
        raise NotEvaluated()

    def parser(document: Document) -> Iterable[Region]:
        yield Region(0, 1, None, evaluator)

    examples, namespace = parse('sample1.txt', parser, expected=1)
    with ShouldRaise(SybilFailure(examples[0], f'{evaluator!r} should not raise NotEvaluated()')):
        examples[0].evaluate()


def test_find_region_sources_bad_end_match():
    path = sample_path('lexing-fail.txt')
    document = Document(Path(path).read_text(), path)
    with ShouldRaise(LexingException(f"Could not match 'END' in {path}:\n'\\nEDN\\n'")):
        tuple(document.find_region_sources(
            start_pattern=re.compile('START'), end_pattern=re.compile('END'),
        ))
