from __future__ import print_function

import re
from functools import partial
from sybil import Sybil, Region
from sybil.integration.unittest import TestCase
from unittest import TestSuite


def check(letter, example):
    print(example.namespace['x'])
    example.namespace['x'] += 1
    text, expected = example.parsed
    actual = text.count(letter)
    if actual != expected:
        message = '{} count was {} instead of {}'.format(
            letter, actual, expected
        )
        if letter == 'X':
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


sb = Sybil(
    [partial(parse_for, 'X'), partial(parse_for, 'Y')],
    path='../pytest', pattern='*.rst',
    setup=sybil_setup, teardown=sybil_teardown
)


def _load_tests(loader=None, tests=None, pattern=None):
    doctests_suites = []
    for path in sorted(sb.path.glob('**/*')):
        if path.is_file() and sb.should_parse(path):
            document = sb.parse(path)

            SybilTestCase = type(
                document.path,
                (TestCase,),
                dict(
                    sybil=sb,
                    namespace=document.namespace,
                ),
            )

            testsuite_of_document = TestSuite()
            examples = [example for example in document]
            stc = SybilTestCase(examples)
            stc.namespace.update(
                {
                    'self': stc,
                },
            )
            testsuite_of_document.addTest(stc)
            # TestSuite can now be layered
            doctests_suites.append(testsuite_of_document)
    return TestSuite(doctests_suites)


load_tests = _load_tests
