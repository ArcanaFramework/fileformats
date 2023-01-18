FileFormats
===========
.. image:: https://github.com/arcanaframework/fileformats/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/arcanaframework/fileformats/actions/workflows/tests.yml
.. image:: https://codecov.io/gh/arcanaframework/fileformats/branch/main/graph/badge.svg?token=UIS0OGPST7
   :target: https://codecov.io/gh/arcanaframework/fileformats
.. image:: https://img.shields.io/pypi/pyversions/fileformats.svg
   :target: https://pypi.python.org/pypi/fileformats/
   :alt: Supported Python versions
.. image:: https://img.shields.io/pypi/v/fileformats.svg
   :target: https://pypi.python.org/pypi/fileformats/
   :alt: Latest Version

*Fileformats* provides Python classes for representing different file formats
for use in type hinting and input validation in data workflows. File formats are
typically identified by a combination of file extension and "magic numbers" where
applicable. However, *Fileformats* provides a flexible framework to write custom
identification routines for exotic file formats, which require deeper inspection of
header files.


Quick Installation
------------------

All sub-packages can be installed by installing the ``fileformats`` meta-package::

    $ python3 -m pip fileformats


Converters
----------

Support for converter methods between several equivalent formats can be installed by
passing the 'converters' install extra, e.g::

    $ python3 -m pip install fileformats[converters]

The converters are implemented in the Pydra_ dataflow framework, and can be linked into
wider Pydra_ workflows using ``DesiredFormat.get_converter(OriginalFormat)``, or
run standalone using the ``DesiredFormat.convert(original_file)`` classmethod.


License
-------

This work is licensed under a
`Creative Commons Attribution 4.0 International License <http://creativecommons.org/licenses/by/4.0/>`_

.. image:: https://i.creativecommons.org/l/by/4.0/88x31.png
  :target: http://creativecommons.org/licenses/by/4.0/
  :alt: Creative Commons Attribution 4.0 International License

.. _Pydra: https://pydra.readthedocs.io
