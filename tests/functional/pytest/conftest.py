from __future__ import print_function
from functools import partial
import re

import pytest

from sybil import Region, Sybil
from sybil.parsers.codeblock import CodeBlockParser


@pytest.fixture(scope="function")
def function_fixture():
    print('function_fixture setup')
    yield 'f'
    print(' function_fixture teardown')


@pytest.fixture(scope="class")
def class_fixture():
    print('class_fixture setup')
    yield 'c'
    print('class_fixture teardown')


@pytest.fixture(scope="module")
def module_fixture():
    print('module_fixture setup')
    yield 'm'
    print('module_fixture teardown')


@pytest.fixture(scope="session")
def session_fixture():
    print('session_fixture setup')
    yield 's'
    print('session_fixture teardown')


def check(letter, example):
    namespace = example.namespace
    for name in (
        'x', 'session_fixture', 'module_fixture',
        'class_fixture', 'function_fixture'
    ):
        print(namespace[name], end='')
    print(end=' ')
    namespace['x'] += 1
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
    print('sybil setup', end=' ')
    namespace['x'] = 0


def sybil_teardown(namespace):
    print('sybil teardown', namespace['x'])


pytest_collect_file = Sybil(
    parsers=[
        partial(parse_for, 'X'),
        partial(parse_for, 'Y'),
        CodeBlockParser(['print_function'])
    ],
    pattern='*.rst',
    setup=sybil_setup, teardown=sybil_teardown,
    fixtures=['function_fixture', 'class_fixture',
              'module_fixture', 'session_fixture']
).pytest()
