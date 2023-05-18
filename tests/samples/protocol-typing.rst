.. code-block:: python

    from typing import Protocol, runtime_checkable

    @runtime_checkable
    class NamedValue(Protocol):
        """Interface for an object that has a name and a value."""

        value: float
        name: str

some text

.. code-block:: python

    class NamedValueClass1:
        def __init__(self, name: str, value: float):
            self.name = name
            self.value = value


    v = NamedValueClass1("foo", 1.0)


::

    >>> isinstance(v, NamedValue)
    True

This above should be ``True``
