from os.path import dirname, join


def sample_path(name):
    return join(dirname(__file__), 'samples', name)
