from os.path import dirname, join

from sybil.document import Document


def sample_path(name):
    return join(dirname(__file__), 'samples', name)


def document_from_sample(name):
    path = sample_path(name)
    with open(path) as source:
        return Document(source.read(), path)
