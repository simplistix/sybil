Quickstart
==========

Here's how you would set up a ``conftest.py`` in the root of your
project such that running `pytest`__ would check examples in your project's source code
and `Sphinx`__ source. Python :rst:dir:`code-block` and :ref:`doctest <doctest-simple-testfile>`
examples will be checked:

__ https://docs.pytest.org

__ https://www.sphinx-doc.org/

.. literalinclude:: examples/quickstart/conftest.py

You'll also want to disable pytest's own doctest plugin by putting this in your pytest config:

.. literalinclude:: examples/quickstart/pytest.ini
    :language: ini

An example of a documentation source file that could be checked using the above
configuration is shown below:

.. literalinclude:: examples/quickstart/example.rst
    :language: rest
