from __future__ import print_function

import re
from functools import partial

from sybil import Sybil, Region


def check(letter, example):
    print(example.namespace['x'])
    example.namespace['x'] += 1
    text, expected = example.parsed
    actual = text.count(letter)
    if actual != expected:
        message = '{} count was {} instead of {}'.format(
            letter, actual, expected
        )
        if letter=='X':
            raise ValueError(message)
        return message


def parse_for(letter, document):
    for m in re.finditer(r'(%s+) (\d+) check' % letter, document.text):
        yield Region(m.start(), m.end(),
                     (m.group(1), int(m.group(2))),
                     partial(check, letter))


def sybil_setup(namespace):
    print('sybil setup')
    namespace['x'] = 0


def sybil_teardown(namespace):
    print('sybil teardown', namespace['x'])


load_tests = Sybil(
    [partial(parse_for, 'X'), partial(parse_for, 'Y')],
    path='../pytest', pattern='*.rst',
    setup=sybil_setup, teardown=sybil_teardown
).unittest()
