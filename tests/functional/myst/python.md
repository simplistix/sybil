# Python examples

A Python example using the normal MD way of specifying a language:

```python
assert 1 + 1 == 2
```

A Python example using a MyST role:

```{code-block} python
assert 1 + 1 == 2
```

Here's one way we could do invisible code blocks:

% invisible-code-block: python
%
% b = 4
%
% # ...etc...


Here's another way we might be able to do them:

<!---  invisible-code-block: python
def foo():
   return 42

meaning_of_life = 42

assert foo() == meaning_of_life
--->

This is an <!-- inline comment -->.

What about a bullet?

- Bullet 1

  ```python
  raise Exception('boom!')
  ```
  
- Bullet 2:

    % skip: next

    <!---  invisible-code-block: python
    
        blank line above ^^ 
        
        blank line below:
    
    --->
