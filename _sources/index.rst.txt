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

This will perform a basic install with minimal dependencies, which can be used for
type validation and detection. To also install the dependencies required to read data
from, and converters between, select file formats, you can install the package with
the ``extended`` option.

.. code-block:: bash

    $ python3 -m pip install fileformats[extended]


Basic Usage
-----------

Validation
~~~~~~~~~~

In the basic case, *FileFormats* can be used for checking the format of files and
directories against known types. There are two layers of checks, ones
performed on the file-system paths alone, which are run when a format class is
initiated, e.g.

.. code-block:: python

    from fileformats.image import Jpeg

    jpeg_file = Jpeg("/path/to/image.jpg")  # Checks path for correct extension

    jpeg_file = Jpeg("/path/to/image.png")  # <-- THIS WILL FAIL as the extension is wrong

The second layer of checks, which typically require reading the file and checking for
magic numbers and the like, are explicitly run by the ``validate`` method.

.. code-block:: python

    fspath = "/path/to/fake-image.jpg"

    with open(fspath, "w") as f:
        f.write("this is not a valid JPEG file")

    jpeg_file = Jpeg(fspath)  # Extension checks out ok
    jpeg_file.validate()  # <-- THIS WILL FAIL as the magic number isn't present


Path handling
~~~~~~~~~~~~~

Once a file object is initiated you are able to access the "required properties" of the
format class, which for single file formats is typically just the file-system path,
``fspath``.

.. code-block:: python

   >>> from fileformats.image import Jpeg
   >>> jpeg_file = Jpeg("/path/to/image.jpg")
   >>> jpeg_file.fspath
   "/path/to/image.jpg"

However, file-formats that consist of multiple files, which is common in scientific
data, will define separate required properties for each file. For example, the
Analyze_ neuroimaging format, which stores the image in a file with the extension
".img" and metadata in a separate header file with the extension ".hdr".

.. code-block:: python

    >>> from fileformats.medimage import Analyze
    >>> analyze_file = Analyze(["/path/to/neuroimage.hdr", "/path/to/neuroimage.img"])
    >>> analyze_file.fspath
    "/path/to/neuroimage.img"
    >>> analyze_file.header
    "/path/to/neuroimage.hdr"

To access all file-system paths in a format object you can access the ``fspaths``
attribute from the base class of all file formats ``fileformats.core.base.FileSet``

.. code-block:: python

    >>> analyze_file.fspaths
    {"/path/to/neuroimage.hdr", "/path/to/neuroimage.img"}

In the case of file formats with "adjacent" files that share the same file-name stem
(such as Analyze_) you only need to provide one the primary paths and the header will be
automatically detected if present and added to the file-set

.. code-block:: python

    >>> from fileformats.medimage import Analyze
    >>> analyze_file = Analyze("/path/to/neuroimage.img")
    >>> analyze_file.fspaths
    {"/path/to/neuroimage.hdr", "/path/to/neuroimage.img"}

This can be useful when reading the output path of a workflow where only primary path
is returned, and both files need to be saved to an output directory. To copy all files
in a format you can use the ``copy_to`` method

.. code-block:: python

    >>> analyze_file_copy = analyze_file.copy_to("/path/to/destination")
    >>> analyze_file_copy.fspaths
    {"/path/to/destination/neuroimage.hdr", "/path/to/destination/neuroimage.img"}

Going the other way from a format class to a workflow/task input, the transformation
of the format object to a path-like string is handled implicitly through the
implementation of the ``__str__`` and ``__fspath__`` magic methods. This means
that format objects can be used in place of the path objects themselves, e.g.

.. code-block:: python

    import subprocess
    from fileformats.text import Plain
    text_file = Plain("/path/to/image.txt")

    with open(text_file) as f:
        contents = f.read()

    subprocess.run(f"cp {text_file} /path/to/destination", shell=True)

Noting that it is only the "primary" path as returned by the ``fspath`` property that
is rendered.

Directory formats
~~~~~~~~~~~~~~~~~

.. warning::
   UNDER CONSTRUCTION


Extended Usage
--------------

.. warning::
   UNDER CONSTRUCTION

.. code-block:: bash

    $ python3 -m pip install fileformats[extended]


.. toctree::
    :maxdepth: 2
    :hidden:

    identification
    extensions


.. _Pydra: https://pydra.readthedocs.io
.. _Analyze: https://en.wikipedia.org/wiki/Analyze_(imaging_software)
