import re

import doctest
from doctest import set_unittest_reportflags
from typing import Any, Dict, List, Optional

from sybil import Example

#: A doctest option flag to limit comparison of numbers in expected output to the precision
#: specified in the example.
NUMBER = doctest.register_optionflag("NUMBER")


class DocTest(doctest.DocTest):
    def __init__(
            self,
            examples: List[doctest.Example],
            globs: Dict[str, Any],
            name: str,
            filename: Optional[str],
            lineno: Optional[int],
            docstring: Optional[str],
        ) -> None:
        # do everything like regular doctests, but don't make a copy of globs
        doctest.DocTest.__init__(self, examples, globs, name, filename, lineno, docstring)
        self.globs = globs


def float_approx_equal(expected: str, actual: str, tolerance: float=1e-12) -> bool:
    return abs(float(expected) - float(actual)) <= tolerance


class OutputChecker(doctest.OutputChecker):
    _number_re = re.compile(
        r"""
        (?P<number>
          (?P<mantissa>
            (?P<integer1> [+-]?\d*)\.(?P<fraction>\d+)
            |
            (?P<integer2> [+-]?\d+)\.
          )
          (?:
            [Ee]
            (?P<exponent1> [+-]?\d+)
          )?
          |
          (?P<integer3> [+-]?\d+)
          (?:
            [Ee]
            (?P<exponent2> [+-]?\d+)
          )
        )
        """,
        re.VERBOSE,
    )

    def _remove_unwanted_precision(self, want: str, got: str) -> str:
        wants = list(self._number_re.finditer(want))
        gots = list(self._number_re.finditer(got))
        if len(wants) != len(gots):
            return got
        offset = 0
        for w, g in zip(wants, gots):
            fraction: Optional[str] = w.group("fraction")
            exponent: Optional[str] = w.group("exponent1")
            if exponent is None:
                exponent = w.group("exponent2")
            if fraction is None:
                precision = 0
            else:
                precision = len(fraction)
            if exponent is not None:
                precision -= int(exponent)
            if float_approx_equal(w.group(), g.group(), tolerance=10 ** -precision):
                # They're close enough. Replace the text we actually
                # got with the text we want, so that it will match when we
                # check the string literally.
                got = (
                        got[: g.start() + offset] + w.group() + got[g.end() + offset:]
                )
                offset += w.end() - w.start() - (g.end() - g.start())
        return got

    def check_output(self, want: str, got: str, optionflags: int) -> bool:
        allow_number = optionflags & NUMBER
        if allow_number:
            got = self._remove_unwanted_precision(want, got)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


class DocTestRunner(doctest.DocTestRunner):

    def __init__(self, optionflags: int) -> None:
        _unittest_reportflags = set_unittest_reportflags(0)
        set_unittest_reportflags(_unittest_reportflags)
        optionflags |= _unittest_reportflags
        doctest.DocTestRunner.__init__(
            self,
            verbose=False,
            optionflags=optionflags,
            checker=OutputChecker(),
        )

    def _failure_header(self, test: DocTest, example: doctest.Example) -> str:
        return ''


class DocTestEvaluator:
    """
    The :any:`Evaluator` to use for :class:`Regions <sybil.Region>` yielded by
    a :class:`~sybil.parsers.abstract.doctest.DocTestStringParser`.


    :param optionflags:
        :ref:`doctest option flags<option-flags-and-directives>` to use
        when evaluating examples.
    """

    def __init__(self, optionflags: int = 0) -> None:
        self.runner = DocTestRunner(optionflags)

    def __call__(self, sybil_example: Example) -> str:
        example = sybil_example.parsed
        namespace = sybil_example.namespace
        output: List[str] = []
        remove_name = False
        try:
            if '__name__' not in namespace:
                remove_name = True
                namespace['__name__'] = '__test__'
            self.runner.run(
                DocTest([example], namespace, name=sybil_example.path,
                        filename=None, lineno=example.lineno, docstring=None),
                clear_globs=False,
                out=output.append
            )
        finally:
            if remove_name:
                del namespace['__name__']
        return ''.join(output)
