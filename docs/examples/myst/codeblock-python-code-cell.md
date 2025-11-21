% invisible-code-block: python
%
%  # This could be some state setup needed to demonstrate things
% initialized = True

This fenced code block defines a function:

```python

    def prefix(text: str) -> str:
        return 'prefix: '+text
```

This MyST `code-cell` directive then uses it:

```{code-cell} python
    prefixed = prefix('some text')
```

<!--- invisible-code-block: python
assert prefixed == 'prefix: some text', prefixed
--->
