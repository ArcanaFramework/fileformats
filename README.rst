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
.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat
   :target: https://arcanaframework.github.io/fileformats/
   :alt: Documentation Status

*FileFormats* provides a library of file-format types implemented as Python classes.
The file-format types can be used in type hinting during the construction
of data workflows (e.g. Pydra_), and used to detect and validate the format of files.
The file-format types


typically identified by a combination of file extension and "magic numbers" where
applicable. However, *Fileformats* provides a flexible framework to write custom
identification routines for exotic file formats, which require deeper inspection of
header files.


Quick Installation
------------------

All sub-packages can be installed from PyPI with::

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
