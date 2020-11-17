from __future__ import absolute_import

import re
from doctest import (
    DocTest as BaseDocTest,
    DocTestParser as BaseDocTestParser,
    DocTestRunner as BaseDocTestRunner,
    Example as DocTestExample,
    OutputChecker as BaseOutputChecker,
    _unittest_reportflags,
    register_optionflag
)

from ..compat import PY3
from ..region import Region


def make_literal(literal):
    return re.compile(literal+r"((['\"])[^\2]*?\2)", re.MULTILINE)


BYTE_LITERAL = make_literal('b')
UNICODE_LITERAL = make_literal('u')


#: A :ref:`doctest option flag<option-flags-and-directives>` that
#: causes byte and unicode literals in doctest expected
#: output to be rewritten such that they are compatible with the version of
#: Python with which the tests are executed.
FIX_BYTE_UNICODE_REPR = register_optionflag('FIX_BYTE_UNICODE_REPR')


class DocTest(BaseDocTest):
    def __init__(self, examples, globs, name, filename, lineno, docstring):
        # do everything like regular doctests, but don't make a copy of globs
        BaseDocTest.__init__(self, examples, globs, name, filename, lineno,
            docstring)
        self.globs = globs


class OutputChecker(BaseOutputChecker):

    def __init__(self, encoding):
        self.encoding = encoding

    def _decode(self, got):
        decode = getattr(got, 'decode', None)
        if decode is None:
            return got
        return decode(self.encoding)

    def check_output(self, want, got, optionflags):
        return BaseOutputChecker.check_output(
            self, want, self._decode(got), optionflags
        )

    def output_difference(self, example, got, optionflags):
        return BaseOutputChecker.output_difference(
            self, example, self._decode(got), optionflags
        )


class DocTestRunner(BaseDocTestRunner):

    def __init__(self, optionflags, encoding):
        optionflags |= _unittest_reportflags
        BaseDocTestRunner.__init__(
            self,
            checker=OutputChecker(encoding),
            verbose=False,
            optionflags=optionflags,
        )

    def _failure_header(self, test, example):
        return ''


def fix_byte_unicode_repr(want):
    if PY3:
        pattern = UNICODE_LITERAL
    else:
        pattern = BYTE_LITERAL
    return pattern.sub(r"\1", want)


class DocTestParser(BaseDocTestParser):
    """
    A class to instantiate and include when your documentation makes use of
    :ref:`doctest-parser` examples.
     
    :param optionflags: 
        :ref:`doctest option flags<option-flags-and-directives>` to use
        when evaluating the examples found by this parser.

    :param encoding:
        If on Python 2, this encoding will be used to decode the string
        resulting from execution of the examples.
    """
    def __init__(self, optionflags=0, encoding='utf-8'):
        self.runner = DocTestRunner(optionflags, encoding)

    def __call__(self, document):
        # a cut down version of doctest.DocTestParser.parse:

        text = document.text
        first_tab = text.find('\t')
        if first_tab != -1:
            raise ValueError('tabs are not supported, first one found at '+(
                document.line_column(first_tab)
            ))
        # If all lines begin with the same indentation, then strip it.
        min_indent = self._min_indent(text)
        if min_indent > 0:
            text = '\n'.join([l[min_indent:] for l in text.split('\n')])

        charno, lineno = 0, 0
        # Find all doctest examples in the string:
        for m in self._EXAMPLE_RE.finditer(text):
            # Update lineno (lines before this example)
            lineno += text.count('\n', charno, m.start())
            # Extract info from the regexp match.
            (source, options, want, exc_msg) = \
                     self._parse_example(m, document.path, lineno)

            if self.runner.optionflags & FIX_BYTE_UNICODE_REPR:
                want = fix_byte_unicode_repr(want)
                if exc_msg:
                    exc_msg = fix_byte_unicode_repr(exc_msg)

            # Create an Example, and add it to the list.
            if not self._IS_BLANK_OR_COMMENT(source):
                yield Region(
                    m.start(),
                    m.end(),
                    DocTestExample(source, want, exc_msg,
                            lineno=lineno,
                            indent=min_indent+len(m.group('indent')),
                            options=options),
                    self.evaluate

                )
            # Update lineno (lines inside this example)
            lineno += text.count('\n', m.start(), m.end())
            # Update charno.
            charno = m.end()

    def evaluate(self, sybil_example):
        example = sybil_example.parsed
        namespace = sybil_example.namespace
        output = []
        self.runner.run(
            DocTest([example], namespace, name=None,
                    filename=None, lineno=example.lineno, docstring=None),
            clear_globs=False,
            out=output.append
        )
        return ''.join(output)
