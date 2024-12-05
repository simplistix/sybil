Development
===========

.. highlight:: bash

If you wish to contribute to this project, then you should fork the
repository found here:

https://github.com/simplistix/sybil/

Once that has been done and you have a checkout, you can follow these
instructions to perform various development tasks:

Setting up a virtualenv
-----------------------

The recommended way to set up a development environment is to create
a virtualenv and then install the package in editable form as follows::

  $ python3 -m venv ~/virtualenvs/sybil
  $ source ~/virtualenvs/sybil/bin/activate
  $ pip install -U pip setuptools
  $ pip install -U -e .[test,docs]

Running the tests
-----------------

Once you've set up a virtualenv, the tests can be run in the activated
virtualenv as follows::

  $ pytest

Building the documentation
--------------------------

The Sphinx documentation is built by doing the following from the
directory containing setup.py::

  $ cd docs
  $ make html

To check that the description that will be used on PyPI renders properly,
do the following::

  $ python setup.py --long-description | rst2html.py > desc.html

The resulting ``desc.html`` should be checked by opening in a browser.

To check that the README that will be used on GitHub renders properly,
do the following::

  $ cat README.rst | rst2html.py > readme.html

The resulting ``readme.html`` should be checked by opening in a browser.

Making a release
----------------

To make a release, just update the version in ``setup.py``,
update the change log, and push to https://github.com/simplistix/sybil
and Carthorse should take care of the rest.
