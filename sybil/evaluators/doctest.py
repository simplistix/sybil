from doctest import (
    DocTest as BaseDocTest,
    DocTestRunner as BaseDocTestRunner,
    _unittest_reportflags,
)

from sybil import Example


class DocTest(BaseDocTest):
    def __init__(self, examples, globs, name, filename, lineno, docstring):
        # do everything like regular doctests, but don't make a copy of globs
        BaseDocTest.__init__(self, examples, globs, name, filename, lineno, docstring)
        self.globs = globs


class DocTestRunner(BaseDocTestRunner):

    def __init__(self, optionflags):
        optionflags |= _unittest_reportflags
        BaseDocTestRunner.__init__(
            self,
            verbose=False,
            optionflags=optionflags,
        )

    def _failure_header(self, test, example):
        return ''


class DocTestEvaluator:
    """
    The :any:`Evaluator` to use for :class:`Regions <sybil.Region>` yielded by
    a :class:`~sybil.parsers.abstract.doctest.DocTestStringParser`.


    :param optionflags:
        :ref:`doctest option flags<option-flags-and-directives>` to use
        when evaluating examples.
    """

    def __init__(self, optionflags=0):
        self.runner = DocTestRunner(optionflags)

    def __call__(self, sybil_example: Example) -> str:
        example = sybil_example.parsed
        namespace = sybil_example.namespace
        output = []
        self.runner.run(
            DocTest([example], namespace, name=sybil_example.path,
                    filename=None, lineno=example.lineno, docstring=None),
            clear_globs=False,
            out=output.append
        )
        return ''.join(output)
