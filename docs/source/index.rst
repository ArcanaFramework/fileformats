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
The format classes are designed to be used in file-type validation during the construction
of data workflows (see Pydra_), and provide a common interface to general methods
for manipulating and moving the underlying file-system objects between storage locations.

Unlike other Python file-type packages, *FileFormats*, supports multi-file
formats, e.g. with separate header/data files, directories containing files of a certain
type, closely related data spread across several files. It also provides limited support
for loading data and metadata, and hooks for conversion methods to be registered between
equivalent data formats.

File-format types are typically identified by a combination of file extensions
and "magic numbers", where applicable. In addition to these generic methods,
*FileFormats* provides a flexible framework to conveniently add custom identification
routines for exotic file formats, e.g. formats that require inspection of headers to
locate other all members of the "file set".

Installation
------------

*FileFormats* can be installed for Python >=3.7 using *pip*

.. code-block:: bash

    $ python3 -m pip install fileformats

To also install dependencies required to run converters between select file formats
use the ``converters`` install extra

.. code-block:: bash

    $ python3 -m pip install fileformats[extended]


.. toctree::
    :maxdepth: 2
    :hidden:

    identification
    extensions
    converters


Basic Usage
-----------

Type Hinting
~~~~~~~~~~~~


Validation
~~~~~~~~~~~~


Manipulation
~~~~~~~~~~~~


.. _Pydra: https://pydra.readthedocs.io
