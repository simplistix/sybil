from ns.module_a import foo


def baz():
    """
    Deliberately doesn't assert its own ``__name__``: under the pytest runner
    pytest itself imports ``regular`` as a top-level package, because it has an
    ``__init__.py``, so this module's name depends on the runner. Sybil defers
    to whatever already worked rather than importing a second copy.

    >>> baz()
    'baz(ns.module_a)'

    """
    return f'baz({foo()})'
