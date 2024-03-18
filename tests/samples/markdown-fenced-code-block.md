backticks:

```
<
 >
```

tildes:
~~~
<
 >
~~~

Fewer than three backticks is not enough:
``
foo
``


The closing code fence must use the same character as the opening fence:


```
aaa
~~~
```


The closing code fence must be at least as long as the opening fence:

````
aaa
```
``````

Nested:

~~~~
~~~
aaa
~~~
~~~~


Can't mix chars:

~`~
foo
~`~


This one gets closed by the end of document:
```
some stuff here
~~~
