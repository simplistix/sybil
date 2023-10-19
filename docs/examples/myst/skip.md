% skip: next

This would be wrong:

```python
>>> 1 == 2
True
```

This is pseudo-code:

% skip: start

```python
def foo(...) -> bool:
    ...
```

When you want to foo, you could do it like this:

```python
foo('baz', 'bob', ...)
```

% skip: end

% invisible-code-block: python
%
%  import sys

This will only work on Python 3:

% skip: next if(sys.version_info < (3, 0), reason="python 3 only")

```python
>>> repr(b'foo')
"b'foo'"
```

This example is not yet working, but I wanted to be reminded:

% skip: next "not yet working"

```python
>>> 1.1 == 1.11
True
```

And here we can see some pseudo-code that will work in a future release:

% skip: start "Fix in v5"

```python
>>> helper = Framework().make_helper()
>>> helper.describe(...)
```

% skip: end

<!-- skip: next -->

This would still be wrong:

```python
>>> 1 == 1
True
```

