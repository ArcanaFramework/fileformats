.. _home:

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
.. image:: https://img.shields.io/github/stars/ArcanaFramework/fileformats?label=GitHub
   :alt: GitHub stars
   :target: https://github.com/ArcanaFramework/fileformats


*Fileformats* provides a library of file-format types implemented as Python classes.
The file-format types can be used in type hinting during the construction
of data workflows (e.g. Pydra_), detect and validate the format of files, and move
sets of related files around the file-system together.

Unlike other file-type Python packages, *FileFormats*, supports multi-file
formats, e.g. with separate header/data files, nested directories. It also provides
limited support for loading metadata/data and conversions between some equivalent
types.

File-format types are typically identified by a combination of file extension
and "magic numbers" where applicable. However, *FileFormats* provides a flexible
framework to add custom identification routines for exotic file formats, e.g.
formats that require inspection of headers, directories containing certain files.
See the `extension template <https://github.com/ArcanaFramework/fileformats-extension-template>`__
for instructions on how to add an extension to the standard types.


.. toctree::
    :maxdepth: 2
    :hidden:

    installation
    mime
    extensions
    converters


.. _Pydra: http://pydra.readthedocs.io
