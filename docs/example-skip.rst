.. skip: next

This would be wrong:

>>> 1 == 2
True

This is pseudo-code:

.. skip: start

>>> foo = ...
>>> foo(..)

.. skip: end

.. invisible-code-block: python

  import sys

This will only work on Python 3:

.. skip: next if(sys.version_info < (3, 0), reason="python 3 only")

>>> repr(b'foo')
"b'foo'"
