import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from unittest import SkipTest

import pytest
from testfixtures import ShouldRaise

from sybil import Sybil, Document
from sybil.parsers.rest import CodeBlockParser, PythonCodeBlockParser, DocTestParser, SkipParser
from .helpers import parse, sample_path


def test_basic():
    examples, namespace = parse('skip.txt', PythonCodeBlockParser(), SkipParser(), expected=9)
    for example in examples:
        example.evaluate()
    assert namespace['run'] == [2, 5]


def test_conditional_edge_cases():
    examples, namespace = parse(
        'skip-conditional-edges.txt', DocTestParser(), SkipParser(), expected=8
    )
    namespace['sys'] = sys
    namespace['run'] = []
    skipped = []
    for example in examples:
        try:
            example.evaluate()
        except SkipTest as e:
            skipped.append(str(e))
    assert namespace['run'] == [1, 2, 3, 4]
    # we should always have one and only one skip from this document.
    assert skipped == ['skip 1']


def test_conditional_full():
    examples, namespace = parse('skip-conditional.txt', DocTestParser(), SkipParser(), expected=11)
    namespace['result'] = result = []
    for example in examples:
        try:
            example.evaluate()
        except SkipTest as e:
            result.append('skip:' + str(e))
    assert result == [
        'start',
        'skip:(2 > 1)',
        'good 1',
        'skip:foo',
        'skip:foo',
        'good 2',
        'skip:good reason',
    ]


def test_bad():
    examples, namespace = parse('skip-conditional-bad.txt', SkipParser(), expected=4)

    with pytest.raises(ValueError) as excinfo:
        examples[0].evaluate()
    assert str(excinfo.value) == 'Bad skip action: lolwut'

    examples[1].evaluate()

    with pytest.raises(ValueError) as excinfo:
        examples[2].evaluate()
    assert str(excinfo.value) == "Cannot have condition on 'skip: end'"

    with pytest.raises(SyntaxError):
        examples[3].evaluate()


def test_start_follows_start():
    examples, namespace = parse('skip-start-start.txt', DocTestParser(), SkipParser(), expected=7)
    namespace['result'] = result = []
    for example in examples[:2]:
        example.evaluate()
    with ShouldRaise(ValueError("'skip: start' cannot follow 'skip: start'")):
        examples[2].evaluate()
    assert result == []


def test_next_follows_start():
    examples, namespace = parse('skip-start-next.txt', DocTestParser(), SkipParser(), expected=7)
    namespace['result'] = result = []
    for example in examples[:2]:
        example.evaluate()
    with ShouldRaise(ValueError("'skip: next' cannot follow 'skip: start'")):
        examples[2].evaluate()
    assert result == []


def test_end_no_start():
    examples, namespace = parse('skip-just-end.txt', DocTestParser(), SkipParser(), expected=3)
    namespace['result'] = result = []
    examples[0].evaluate()
    with ShouldRaise(ValueError("'skip: end' must follow 'skip: start'")):
        examples[1].evaluate()
    assert result == ['good']


def test_next_follows_next():
    examples, namespace = parse('skip-next-next.txt', DocTestParser(), SkipParser(), expected=4)
    namespace['result'] = result = []
    for example in examples:
        example.evaluate()
    assert result == [1]


_SKIP_NEXT_RST = (
    "Title\n=====\n\n"
    ".. code-block:: python\n\n   x = 1\n\n"
    ".. skip: next\n\n"
    ".. code-block:: python\n\n   bad_undefined_name\n\n"
    ".. code-block:: python\n\n   y = 2\n"
)


def test_skip_next_resolves_by_document_order_not_evaluation_order(
    tmp_path: Path,
) -> None:
    path = tmp_path / "doc.rst"
    path.write_text(_SKIP_NEXT_RST)

    ran: list[int] = []
    sybil = Sybil(
        parsers=[
            SkipParser(),
            CodeBlockParser("python", lambda e: ran.append(e.line)),
        ],
    )
    examples = list(sybil.parse(path=path).examples())
    for example in reversed(examples):
        example.evaluate()
    assert sorted(ran) == [4, 14], sorted(ran)


def test_concurrent_skip_next(tmp_path: Path) -> None:
    # Under stock CPython the GIL tends to serialise the small ops in
    # Skipper enough to hide the underlying ordering bug, so this test
    # rarely fails against unfixed code on a standard interpreter. It
    # reliably reproduces under free-threaded CPython (e.g. 3.13t), and
    # exercises the locking paths in either case.
    path = tmp_path / "doc.rst"
    path.write_text(_SKIP_NEXT_RST)

    for _ in range(50):
        ran: list[int] = []
        sybil = Sybil(
            parsers=[
                SkipParser(),
                CodeBlockParser("python", lambda e, ran=ran: ran.append(e.line)),
            ],
        )
        examples = list(sybil.parse(path=path).examples())
        with ThreadPoolExecutor(max_workers=len(examples)) as pool:
            futures = [pool.submit(e.evaluate) for e in examples]
            for future in as_completed(futures):
                future.result()
        assert sorted(ran) == [4, 14], sorted(ran)


def test_malformed_arguments():
    path = sample_path('skip-malformed-arguments.txt')
    with ShouldRaise(ValueError("malformed arguments to skip: '<:'")):
        Document.parse(path, SkipParser())


def test_missing_arguments():
    path = sample_path('skip-missing-arguments.txt')
    with ShouldRaise(ValueError("missing arguments to skip")):
        Document.parse(path, SkipParser())
