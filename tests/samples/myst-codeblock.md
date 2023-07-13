This is a code block:

```python

    y += 1
```

After this text is a code block that goes boom:

```{code-block} python
    raise Exception('boom!')
```

Now we have an invisible code block, great for setting things up or checking
stuff within a doc:


% invisible-code-block: python
%
%  z += 1
[__init__.py](..%2F..%2Fsybil%2Fparsers%2Fmyst%2F__init__.py)
This paranoidly checks that we can use binary and unicode literals:

<!--- invisible-code-block: python
bin = b'x'
uni = u'x'
--->

- Here's a code block that should still be found!:

  ```python

    class NoVars:
         __slots__ = ['x']
  ```
  
  This one has some text after it that also forms part of the bullet.

- Another bullet:

  ```{code-block} python

    define_this = 1

  ```
- A following bullet straight away!

- A code block in a non-python language:

  ```lolcode

    HAI
    CAN HAS STDIO?
    VISIBLE "HAI WORLD!"
    KTHXBYE
  ```
- Here's another code block that should still be found, even though it's
  at the end of the document, so don't add more after it!:

  ```python

    class YesVars:
         __slots__ = ['x']

  ```
