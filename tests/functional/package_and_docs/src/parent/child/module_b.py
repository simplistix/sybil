from parent import parent_init


def foo(text):
    """
    >>> parent_init('module_a.foo(parent_init)')
    'module_a.foo(parent_init:module_a.foo(parent_init))'
    """
