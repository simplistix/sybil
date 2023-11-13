This one has arguments a a "title" and then the body:

```{note} This is a note admonition.
This is the second line of the first paragraph.

- The note contains all indented body elements
  following.
- It includes this bullet list.
```

```{admonition} And, by the way...
   You can make up your own admonition too.
```

```{sample}
   This directive has no arguments, just a body.
```

An image with no body followed by one that has params and a body:

```{image} picture.png
```

```{image} picture.jpeg
 :height: 100px
 :width:200 px
 :scale:  50 %
 :alt: alternate text
 :align: right


```

```{figure} picture.png
---
scale: 50 %
alt: map to buried treasure
---
This is the caption of the figure (a simple paragraph).

The legend consists of all elements after the caption.  In this
case, the legend consists of this paragraph and the following
table:

+-----------------------+-----------------------+
| Symbol                | Meaning               |
+=======================+=======================+
| .. image:: tent.png   | Campground            |
+-----------------------+-----------------------+
| .. image:: waves.png  | Lake                  |
+-----------------------+-----------------------+
| .. image:: peak.png   | Mountain              |
+-----------------------+-----------------------+

```


```{topic} Topic Title

    Subsequent indented lines comprise
    the body of the topic, and are
    interpreted as body elements.
```

Now a topic with a class, as used by testfixtures:

```{topic} example.cfg
---
class: read-file
---

 ::

   [A Section]
   dir = frob
```

Another example:

```{sidebar} Optional Sidebar Title
---
  subtitle: Optional Sidebar Subtitle
---
   Subsequent indented lines comprise
   the body of the sidebar, and are
   interpreted as body elements.
```


```{code-block} python
---
lineno-start: 10
emphasize-lines: 1, 3
caption: |
    This is my
    multi-line caption. It is *pretty nifty* ;-)
---
a = 2
print('my 1st line')
print(f'my {a}nd line')
```

```{eval-rst}
.. figure:: img/fun-fish.png
  :width: 100px
  :name: rst-fun-fish

  Party time!

A reference from inside: :ref:`rst-fun-fish`

A reference from outside: :ref:`syntax/directives/parsing`
```
