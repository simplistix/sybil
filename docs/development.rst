Development
===========

.. highlight:: bash

This package is developed using continuous integration which can be
found here:

https://travis-ci.org/cjw296/sybil

The latest development version of the documentation can be found here:

http://sybil.readthedocs.org/en/latest/

If you wish to contribute to this project, then you should fork the
repository found here:

https://github.com/cjw296/sybil/

Once that has been done and you have a checkout, you can follow these
instructions to perform various development tasks:

Setting up a virtualenv
-----------------------

The recommended way to set up a development environment is to turn
your checkout into a virtualenv and then install the package in
editable form as follows::

  $ virtualenv .
  $ bin/pip install -U -e .[test,build]

Running the tests
-----------------

Once you've set up a virtualenv, the tests can be run as follows::

  $ bin/pytest

Building the documentation
--------------------------

The Sphinx documentation is built by doing the following from the
directory containing setup.py::

  $ source bin/activate
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
update the change log, tag it
and push to https://github.com/cjw296/sybil
and Travis CI should take care of the rest.

Once Travis CI is done, make sure to go to
https://readthedocs.org/projects/sybil/versions/
and make sure the new release is marked as an Active Version.
