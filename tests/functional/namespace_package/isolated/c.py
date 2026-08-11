def spam():
    """
    `isolated` is NOT on sys.path and has no `__init__.py` -- structurally
    identical to a namespace package portion, because the directory above it
    is on sys.path. Nothing tells the two apart, so this gets imported under a
    name its author never chose. That is why opting in is required.

    >>> spam()
    'isolated.c'

    """
    return __name__
