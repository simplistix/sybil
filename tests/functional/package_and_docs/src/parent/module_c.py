from . import foo


def bar(text):
    """
    >>> foo('something')
    'module_a.foo(something)'

    >>> bar('something')
    'barmodule_a.foo(something)'

    """
    return 'bar'+foo(text)
