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
of data workflows (e.g. Pydra_, Fastr_), and provide a common interface to general methods
for manipulating and moving the underlying file-system objects between storage locations.

Unlike other file-type Python packages, *FileFormats*, supports multi-file data
formats ("file sets") often found in scientific workflows, e.g. with separate header/data
files, directories containing certain file types, and mechanisms to peek at metadata fields
to define complex data formats or specific sub-types (e.g. functional MRI DICOM file set).

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

This will perform a basic install with minimal dependencies, which can be used for
type validation and detection. To also install the dependencies required to read data
from, and converters between, select file formats, you can install the package with
the ``extended`` option.

.. code-block:: bash

    $ python3 -m pip install fileformats[extended]


.. toctree::
    :maxdepth: 2
    :hidden:

    workflows
    identification
    developer


Quick Example
-------------

Validate an mp4 audio file

.. code-block:: python

   >>> from fileformats.audio import Mp4
   >>> mp4_file = Mp4("/path/to/audio.mp4")
   >>> mp4_file.validate()
   >>> mp4_file.fspath
   "/path/to/audio.mp4"


License
-------

This work is licensed under a
`Creative Commons Attribution 4.0 International License <http://creativecommons.org/licenses/by/4.0/>`_

.. image:: https://i.creativecommons.org/l/by/4.0/88x31.png
  :target: http://creativecommons.org/licenses/by/4.0/
  :alt: Creative Commons Attribution 4.0 International License


.. _Pydra: https://pydra.readthedocs.io
.. _Fastr: https://gitlab.com/radiology/infrastructure/fastr
