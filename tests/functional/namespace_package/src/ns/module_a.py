def foo():
    """
    `src/ns` has no `__init__.py` and `src` is on sys.path, so this is a real
    PEP 420 namespace package and the module is `ns.module_a`, not `module_a`.

    >>> foo()
    'ns.module_a'

    """
    return __name__
