class Checker(object):

    def __call__(self, name):
        assert name=='foo'

    def __iter__(self):
        yield self, 'foo'
        yield self, 'foo'
        yield self, 'foo'


def test_docs():
    for test in Checker():
        yield test
