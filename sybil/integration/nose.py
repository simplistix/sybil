def check(example):
    example.evaluate()


def nose_integration(sybil, name):

    def test_examples():
        for example in sybil.all_examples():
            yield check, example

    if name:
        test_examples.__name__ = name

    return test_examples
