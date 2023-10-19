Here's a simple fenced code block:

```python
>>> 1+1
2
```

Here's a fenced code block forming a MyST role:

```{code-block} python
>>> 1 + 1
3
```

Here's a fleshed out MyST directive:

```{directivename} arguments
---
key1: val1
key2: val2
---
This is
directive content
```

Here's the eval-rst role with a nexted Shinx role:

```{eval-rst}
.. doctest::

    >>> 1 + 1
    4
```

Here's an example of one way we could do "invisible directives":

% invisible-code-block: python
%
% b = 5
%
% ...etc...

This is the same style, but indented and is parsed out for pragmatic reasons:

    % code-block: py
    %
    %   b = 6
    %   ...etc...
    %   

Here's another way we might be able to do them:

<!---  invisible-code-block: python
  def foo():
     return 42

  meaning_of_life = 42

  assert foo() == meaning_of_life()
--->

This is the same style, but indented and is parsed out for pragmatic reasons:

    <!---  code-block: python
    
        blank line above ^^
        
        blank line below:
    
    --->

This is an <!-- inline comment -->.

- This one is in a bullet list so should be picked up (typo deliberate!).

  ```pthon
  assert 1 + 1 == 2
  ```

- Here's one indented because it's in a bullet list:

    <!---  invisible-code: py
    
        blank line above ^^
        
        blank line below:
    
    --->

- Directives can also be indented for the same reason:

  ```{foo} bar
  ---
  key1: val1
  ---
  This, too, is a directive content
  ```


<!-- skip: next -->

<!-- skip: start if("some stuff here", reason='Something') -->

<!-- 
skip: and 
-->

<!-- 
; skip: end 



Other stuff here just gets ignored

-->

<!--  ; skip: also  -->


<!-- clear-namespace -->
