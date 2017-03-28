from __future__ import absolute_import

from nose.plugins import Plugin as NosePlugin
from nose.loader import TestLoader


class SybilLoader(TestLoader):

    def __init__(self, test_suite_func, config):
        super(SybilLoader, self).__init__(config)
        self.test_suite_func = test_suite_func

    def loadTestsFromModule(self, module, path=None, discovered=False):
        suite_func = getattr(module, self.test_suite_func, None)
        if suite_func is not None:
            return suite_func()

        return super(SybilLoader, self).loadTestsFromModule(
            module, path, discovered
            )


class Plugin(NosePlugin):

    name = 'sybil'

    enabled = True

    def options(self, parser, env):
        parser.add_option(
            "--test-suite-func", action="store",
            dest="test_suite_func",
            default='load_tests',
            help="A function in modules that will return a TestSuite. "
                 "Defaults to 'load_tests'.")

    def configure(self, options, config):
        self.test_suite_func = options.test_suite_func

    def prepareTestLoader(self, loader):
        return SybilLoader(self.test_suite_func, loader.config)
