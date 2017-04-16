from os.path import dirname, join

from sybil.document import Document
from sybil.example import Example


def sample_path(name):
    return join(dirname(__file__), 'samples', name)


def document_from_sample(name):
    path = sample_path(name)
    with open(path) as source:
        return Document(source.read(), path)


def evaluate_region(region, namespace):
    return region.evaluator(Example(
        document=Document('', '/the/path'),
        line=0,
        column=0,
        region=region,
        namespace=namespace
    ))
