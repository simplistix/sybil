# Python examples

A Python example using the normal MD way of specifying a language:

```python
assert 1 + 1 == 2
```

Here's the way to do invisible python code blocks:

<!---  invisible-code-block: python
def foo():
   return 42

meaning_of_life = 42

assert foo() == meaning_of_life
--->

This is an <!-- inline comment -->.

What about a bullets?

- Bullet 1

  ```python
  raise Exception('boom!')
  ```
  
- Bullet 2:

    <!-- skip: next -->

    <!---  invisible-code-block: python
    
        blank line above ^^ 
        
        blank line below:
    
    --->
