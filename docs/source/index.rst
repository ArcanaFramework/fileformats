.. _home:

FileFormats
===========
.. image:: https://github.com/arcanaframework/fileformats/actions/workflows/ci-cd.yml/badge.svg
   :target: https://github.com/arcanaframework/fileformats/actions/workflows/ci-cd.yml
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
locate other members of the "file set".

Base features are available for all types within *FileFormats* and its extension
packages using the base install. They are designed to be broadly available for a large
range of types and very light-weight in terms of external dependencies. Additional
features requiring dependencies are implemented in *extras* packages that can be
installed if required.


Installation
------------

*FileFormats* can be installed for Python >=3.7 using *pip*

.. code-block:: console

    $ python3 -m pip install fileformats

This will perform a basic install with minimal dependencies, which can be used for
type validation and detection. To also install the dependencies required to read data
from, and converters between, select file formats, you can install the ``extras`` package.

.. code-block:: console

    $ python3 -m pip install fileformats-extras

The main fileformats package covers all formats specified in the IANA MIME type standard.
However, it has been designed to be able to be extended to file formats used in specialised
domains. These formats are implemented in extension packages such as
`fileformats-medimage <https://github.com/ArcanaFramework/fileformats-medimage>`__ and
`fileformats-datascience <https://github.com/ArcanaFramework/fileformats-datascience>`__,
which can be installed with

.. code-block:: bash

    $ python3 -m pip install fileformats-medimage fileformats-datascience

As with the main package, some extra functionality is available within "extras" packages
for these extensions, which can be installed with

.. code-block:: bash

    $ python3 -m pip install fileformats-medimage-extras fileformats-datascience-extras

.. note::
   See the :ref:`Developer Guide` for instructions on how to implement your own extensions
   and extras.


License
-------

This work is licensed under a
`Creative Commons Attribution 4.0 International License <http://creativecommons.org/licenses/by/4.0/>`_

.. image:: https://i.creativecommons.org/l/by/4.0/88x31.png
  :target: http://creativecommons.org/licenses/by/4.0/
  :alt: Creative Commons Attribution 4.0 International License


.. toctree::
    :maxdepth: 2
    :hidden:

    quick_start
    detection
    mime
    file_handling
    classifiers
    extras
    developer

.. toctree::
   :maxdepth: 2
   :caption: Reference
   :hidden:

   api.rst


.. _Pydra: https://pydra.readthedocs.io
.. _Fastr: https://gitlab.com/radiology/infrastructure/fastr
