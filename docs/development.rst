Development
===========

.. highlight:: bash

If you wish to contribute to this project, then you should fork the
repository found here:

https://github.com/simplistix/sybil/

Once that has been done and you have a checkout,
you can follow the instructions below to perform various development tasks.

For detailed development guidelines, code style requirements, and additional commands,
see ``AGENTS.md`` in the repository root.

Setting up a development environment
-------------------------------------

The recommended way to set up a development environment is to use `uv`__
to install all groups and extras:

__ https://docs.astral.sh/uv/

.. code-block:: bash

    uv sync --dev --all-extras

Running the tests
-----------------

Once you've set up the environment, the tests can be run from the root of a
source checkout as follows:

.. code-block:: bash

  uv run pytest

Building the documentation
--------------------------

The Sphinx documentation is built by doing the following from the
repository root:

.. code-block:: bash

  cd docs
  make html

Making a release
----------------

To make a release, just update the version in ``pyproject.toml``, update the change log
in ``CHANGELOG.rst`` and push to https://github.com/simplistix/sybil.
Carthorse should take care of the rest.
