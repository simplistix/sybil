.. currentmodule:: sybil

Patterns of Use
===============

.. invisible-code-block: python

  from tests.helpers import check_tree

Several commons patterns of use for Sybil are covered here.

Documentation and source examples in Restructured Text
------------------------------------------------------

If your project looks like this::

    ├─docs/
    │ ├─conf.py
    │ └─index.rst
    ├─src/
    │ └─myproj/
    │   └─__init__.py
    ├─conftest.py
    ├─pytest.ini
    └─setup.py

.. --> tree

.. invisible-code-block: python

  check_tree(tree, 'examples/rest_text_rest_src')

And if your documentation looks like this:

.. literalinclude:: examples/rest_text_rest_src/docs/index.rst
  :language: rest

With your examples in source code looking like this:

.. literalinclude:: examples/rest_text_rest_src/src/myproj/__init__.py

Then the following configuration in a ``conftest.py`` will ensure all
your examples are correct:

.. literalinclude:: examples/rest_text_rest_src/conftest.py


Documentation in MyST and source examples in Restructured Text
--------------------------------------------------------------

If your project looks like this::

    ├─docs/
    │ ├─conf.py
    │ └─index.md
    ├─src/
    │ └─myproj/
    │   └─__init__.py
    ├─conftest.py
    ├─pytest.ini
    └─setup.py

.. --> tree

.. invisible-code-block: python

  check_tree(tree, 'examples/myst_text_rest_src')

And if your documentation looks like this:

.. literalinclude:: examples/myst_text_rest_src/docs/index.md
  :language: markdown

With your examples in source code looking like this:

.. literalinclude:: examples/myst_text_rest_src/src/myproj/__init__.py

Then the following configuration in a ``conftest.py`` will ensure all
your examples are correct:

.. literalinclude:: examples/myst_text_rest_src/conftest.py

.. _namespace-packages:

Source in a namespace package
-----------------------------

A project that uses :pep:`420` namespaces will have a layout as follows, where ``myorg`` has
no ``__init__.py``::

    ├─src/
    │ └─myorg/
    │   ├─config.py
    │   └─greeting.py
    ├─conftest.py
    └─pyproject.toml

.. --> tree

.. invisible-code-block: python

  check_tree(tree, 'examples/namespace_package')

A ``pyproject.toml`` such as the following then tells the build backend where the package is.
Installing it in editable mode, such as with ``pip install -e .``, results in ``src`` being added
to :data:`sys.path`.

.. literalinclude:: examples/namespace_package/pyproject.toml
  :language: toml

When your examples in ``src/myorg/greeting.py`` look like this:

.. literalinclude:: examples/namespace_package/src/myorg/greeting.py

Then the following configuration in a ``conftest.py`` will ensure all
your examples are correct:

.. literalinclude:: examples/namespace_package/conftest.py

Without the ``document_types`` mapping, Sybil works out the module's name by walking up to the
first directory without an ``__init__.py``. That stops *inside* the namespace package, so
``greeting.py`` would be imported as ``greeting`` rather than ``myorg.greeting``, and every
example in it would fail with::

    ImportError: 'greeting' not importable from .../src/myorg/greeting.py as:
    ModuleNotFoundError: No module named 'greeting'

:class:`~sybil.document.NamespacePackageDocument` isn't the default because nothing distinguishes
a namespace package from an ordinary directory of modules: Python will import any directory
without an ``__init__.py`` as a namespace package, provided the directory above it is on
:data:`sys.path`. For example, when your project root is on :data:`sys.path`, as it often is during
a test run, :class:`~sybil.document.NamespacePackageDocument` would incorrectly import
``scripts/tool.py`` as ``scripts.tool``.

Linting and checking examples
-----------------------------

If you wish to perform linting of examples in addition to checking that they are correct,
you will need to parse each documentation file once for linting and once for checking.

This can be done by having one :class:`Sybil` to do the linting and another :class:`Sybil`
to do the checking.

Given documentation that looks like this:

.. literalinclude:: examples/linting_and_checking/index.rst

Then the following configuration in a ``conftest.py`` could be used to ensure all
your examples are both correct and lint-free:

.. literalinclude:: examples/linting_and_checking/conftest.py


.. _migrating-from-sphinx.ext.doctest:

Migrating from sphinx.ext.doctest
---------------------------------

Sybil currently has partial support for
:external+sphinx:doc:`sphinx.ext.doctest <usage/extensions/doctest>`.
The list below shows how to approach migrating or supporting the various
directives from ``sphinx.ext.doctest``. Adding further support won't be hard,
so if anything is missing that's holding you back, please open an issue on `GitHub`__.
After that, it's mainly left to stop running ``make doctest``!

__ https://github.com/simplistix/sybil/issues

- :rst:dir:`testsetup` can be replaced with :ref:`invisible-code-block <codeblock-parser>`.

- :rst:dir:`testcleanup` can be replaced with :ref:`invisible-code-block <codeblock-parser>`.

- :rst:dir:`doctest` is supported using the :class:`~sybil.parsers.rest.DocTestDirectiveParser`
  as described in the :ref:`doctest-parser` section.
  Some of the options aren't supported, but their behaviour can be replaced by preceding the
  ``doctest`` with a :ref:`skip <skip-parser>` directive.

- :rst:dir:`testcode` and :rst:dir:`testoutput` would need parsers and evaluators to be written,
  however, they could probably just be replaced with a :ref:`doctest-parser` block.

- ``groups`` aren't supported, but you can achieve test isolation using
  :ref:`clear-namespace <clear-namespace>`.
