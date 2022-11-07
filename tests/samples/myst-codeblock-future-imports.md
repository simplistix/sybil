<!--- invisible-code-block: python

  raise Exception('Boom 1')
--->
More likely is one down here:

```python

  raise Exception('Boom 2')
```
This will keep working but not be an effective test once PEP 563 finally lands:

```{code-block} python

    def foo(x: str):
        print(x)
```
