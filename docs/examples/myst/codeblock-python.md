% invisible-code-block: python
%
%  # This could be some state setup needed to demonstrate things
% initialized = True

This fenced code block defines a function:

```python

    def prefix(text: str) -> str:
        return 'prefix: '+text
```

This MyST `code-block` directive then uses it:

```{code-block} python
    prefixed = prefix('some text')
```

<!--- invisible-code-block: python
assert prefixed == 'prefix: some text', prefixed
--->
