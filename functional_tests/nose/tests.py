class Sybil(object):

    def __call__(self, name):
        assert name=='foo'

    def __iter__(self):
        yield 'foo'
        yield 'foo'
        yield 'foo'

    @property
    def nose(self):
        def test_docs():
            for name in self:
                yield self, name
        return test_docs


test_docs = Sybil().nose
