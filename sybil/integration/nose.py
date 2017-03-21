def check(example, namespace):
    example.evaluate(namespace)


def nose_integration(sybil, name):

    def test_examples():
        namespace = {}
        for example in sybil.all_examples():
            yield check, example, namespace

    if name:
        test_examples.__name__ = name

    return test_examples
