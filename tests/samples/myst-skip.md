```python

  run = []
```

Let's skips some stuff:

% skip: next

After this text is a code block that goes boom, it should be skipped:

```python

  run.append(1)
```

This one should run:

```python

  run.append(2)
```

% skip: start

These should not:

```python

  run.append(3)
```

Nor this one:

```python

  run.append(4)
```

% skip: end

But this one should:

```python

  run.append(5)
```
