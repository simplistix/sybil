# DocTest examples

A Python REPL / DocTest example using normal way of specifying Python
language:

```python
>>> 1+1
2
```

A Python REPL / DocTest example using a MyST role:

```{code-block} python
>>> 1 + 1
2
```

A Python REPL / DocTest example using the `{eval-rst}` role and the `.. doctest::` role
from `sphinx.ext.doctest`:


```{eval-rst}
.. doctest::

    >>> 1 + 1
    3
```


```{doctest}
>>> 1 + 1
4
```
