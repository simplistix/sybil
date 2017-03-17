import re
from functools import partial
from sybil import Region, Sybil


def check(letter, parsed, namespace):
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


pytest_collect_file = Sybil(
    parsers=[partial(parse_for, 'X'), partial(parse_for, 'Y')],
    pattern='*.rst'
).pytest()
