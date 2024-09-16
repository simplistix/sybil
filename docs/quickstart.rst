Quickstart
==========

Sybil is installed as a standard Python package in whatever way works best for you.
If you're using it with `pytest`__, you should install it with the ``pytest`` extra, to ensure
you have compatible versions:

__ https://docs.pytest.org

.. code-block:: bash

  pip install sybil[pytest]

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
