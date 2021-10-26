"""
This one tests that the first example in a .py is actually evaluated
rather than being skipped!

>>> print('bad')
good

"""
from .child.module_a import foo


def parent_init(text):
    """
    >>> 1==1
    True

    """
    return foo('parent_init:'+text)

