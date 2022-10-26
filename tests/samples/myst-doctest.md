# DocTest examples

A Python REPL / DocTest example using normal way of specifying Python
language:

```python
>>> x = 1+1
>>> x
2
```

A Python REPL / DocTest example using a MyST directive:

```{code-block} python
>>> x += 1; x
3
```

A Python REPL / DocTest example using the `{eval-rst}` role and the `.. doctest::` role
from `sphinx.ext.doctest`:


```{eval-rst}
.. doctest::

    >>> 1 + 1
    3

```


```{doctest}
>>> y = 2
>>> raise Exception('uh oh')
Traceback (most recent call last):
...
Exception: uh oh
```

Normal pass followed by a mismatch with expected:

```{doctest}
>>> y == 2
True
>>> y
3
```
