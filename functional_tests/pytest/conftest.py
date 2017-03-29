from __future__ import print_function
import re
from functools import partial
from sybil import Region, Sybil


def check(letter, parsed, namespace):
    print(namespace['x'], end=' ')
    namespace['x'] += 1
    text, expected = parsed
    actual = text.count(letter)
    if actual != expected:
        message = '{} count was {} instead of {}'.format(
            letter, actual, expected
        )
        if letter=='X':
            raise ValueError(message)
        return message


def parse_for(letter, document):
    for m in re.finditer('(%s+) (\d+) check' % letter, document.text):
        yield Region(m.start(), m.end(),
                     (m.group(1), int(m.group(2))),
                     partial(check, letter))


def sybil_setup(namespace):
    print('sybil setup', end=' ')
    namespace['x'] = 0


def sybil_teardown(namespace):
    print(' sybil teardown', namespace['x'], end=' ')


pytest_collect_file = Sybil(
    parsers=[partial(parse_for, 'X'), partial(parse_for, 'Y')],
    pattern='*.rst',
    setup=sybil_setup, teardown=sybil_teardown
).pytest()
