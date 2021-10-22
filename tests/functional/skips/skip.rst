.. invisible-code-block: python

  run = []

Let's skips some stuff:

.. skip: next

After this text is a code block that goes boom, it should be skipped:

.. code-block:: python

  run.append(1)

This one should run:

.. invisible-code-block: python

  run.append(2)

.. skip: start

These should not:

.. code-block:: python

  run.append(3)

Nor this one:

.. code-block:: python

  run.append(4)

.. skip: end

But this one should:

.. code-block:: python

  run.append(5)


Let's make sure things worked!

>>> print(run)
[2, 5]
