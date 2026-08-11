"""
A regular package nested inside the namespace package.

>>> from ns.regular import bar
>>> bar()
'ns.regular'

"""


def bar():
    return __name__
