import re
import string
from textwrap import dedent

from sybil import Region
from sybil.compat import StringIO

CAPTURE_DIRECTIVE = re.compile(
    r'^(?P<indent>(\t| )*)\.\.\s*-+>\s*(?P<name>\S+).*$'
)


def evaluate_capture(example):
    name, text = example.parsed
    example.namespace[name] = text


def indent_matches(line, indent):
    # Is the indentation of a line match what we're looking for?

    if not line.strip():
        # the line consists entirely of whitespace (or nothing at all),
        # so is not considered to be of the appropriate indentation
        return False

    if line.startswith(indent):
        if line[len(indent)] not in string.whitespace:
            return True

    # if none of the above found the indentation to be a match, it is
    # not a match
    return False


class DocumentReverseIterator(list):

    def __init__(self, document):
        # using splitlines(keepends=True) would be more explicit
        # but Python 2 :-(
        self[:] = StringIO(document.text)
        self.current_line = len(self)
        self.current_line_end_position = len(document.text)

    def __iter__(self):
        while self.current_line > 0:
            self.current_line -= 1
            line = self[self.current_line]
            self.current_line_end_position -= len(line)
            yield self.current_line, line


def parse_captures(document):
    """
    A parser function to be included when your documentation makes use of
    :ref:`capture-parser` examples.
    """
    lines = DocumentReverseIterator(document)

    for end_index, line in lines:

        directive = CAPTURE_DIRECTIVE.match(line)
        if directive:

            region_end = lines.current_line_end_position

            indent = directive.group('indent')
            for start_index, line in lines:
                if indent_matches(line, indent):
                    # don't include the preceding line in the capture
                    start_index += 1
                    break
            else:
                # make it blow up
                start_index = end_index

            if end_index - start_index < 2:
                raise ValueError((
                    "couldn't find the start of the block to match"
                    "%r on line %i of %s"
                ) % (directive.group(), end_index+1, document.path))

            # after dedenting, we need to remove excess leading and trailing
            # newlines, before adding back the final newline that's strippped
            # off
            text = dedent(''.join(lines[start_index:end_index])).strip()+'\n'

            name = directive.group('name')
            parsed = name, text

            yield Region(
                lines.current_line_end_position,
                region_end,
                parsed,
                evaluate_capture
            )
