def check(example, namespace):
    errors = example.evaluate(namespace)
    if errors:
        raise AssertionError((
            'Example at {}, line {}, column {} did not evaluate as expected:\n'
            '{}'
        ).format(example.path, example.line, example.column, errors))


def nose_integration(sybil, name):

    def test_examples():
        namespace = {}
        for example in sybil.all_examples():
            yield check, example, namespace

    if name:
        test_examples.__name__ = name

    return test_examples
