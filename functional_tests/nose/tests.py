import re
from functools import partial

from sybil import Sybil, Region


def check(letter, parsed, namespace):
    text, expected = parsed
    assert set(text) == {letter}
    actual = text.count(letter)
    if actual != expected:
        return '{} count was {} instead of {}'.format(
            letter, actual, expected
        )


def parse_for_x(document):
    for m in re.finditer('(X+) (\d+) check', document.text):
        yield Region(m.start(), m.end(),
                     (m.group(1), int(m.group(2))),
                     partial(check, 'X'))


def parse_for_y(document):
    for m in re.finditer('(Y+) (\d+) check', document.text):
        yield Region(m.start(), m.end(),
                     (m.group(1), int(m.group(2))),
                     partial(check, 'Y'))


test_docs = Sybil(
    [parse_for_x, parse_for_y],
    path='../../tests/samples', pattern='*.txt'
).nose(name='test_docs')
