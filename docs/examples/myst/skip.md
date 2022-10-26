; skip: next

This would be wrong:

```python
>>> 1 == 2
True
```

This is pseudo-code:

; skip: start

```python
def foo(...) -> bool:
    ...
```

When you want to foo, you could do it like this:

```python
foo('baz', 'bob', ...)
```

; skip: end

% invisible-code-block: python
%
%  import sys

This will only work on Python 3:

; skip: next if(sys.version_info < (3, 0), reason="python 3 only")

```python
>>> repr(b'foo')
"b'foo'"
```
