class SybilFailure(AssertionError):

    def __init__(self, example, result):
        super(SybilFailure, self).__init__((
            'Example at {}, line {}, column {} did not evaluate as expected:\n'
            '{}'
        ).format(example.path, example.line, example.column, result))
        self.example = example
        self.result = result


class Example(object):

    def __init__(self, path, line, column, region, namespace):
        self.path = path
        self.line = line
        self.column = column
        self.region = region
        self.namespace = namespace

    def __repr__(self):
        return '<Example path={} line={} column={} using {!r}>'.format(
            self.path, self.line, self.column, self.region.evaluator
        )

    def evaluate(self):
        result = self.region.evaluator(self.region.parsed, self.namespace)
        if result:
            raise SybilFailure(self, result)
