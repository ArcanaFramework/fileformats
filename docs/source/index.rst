.. _home:

FileFormats
===========

*Fileformats* provides a library of file-format types implemented as Python classes.
The file-format types can be used in type hinting during the construction
of data workflows (e.g. Pydra_), and used to detect and validate the format of files.
Unlike other file-type Python packages, *FileFormats*, handles multi-file/directory
formats (e.g. with separate header files), and can be used to move such "file sets"
around the file system together.

File-format types are typically identified by a combination of file extension
and "magic numbers" where applicable. However, *FileFormats* provides a flexible
framework to add custom identification routines for exotic file formats, e.g.
formats that require inspection of headers to find the location of data files.


Installation
------------

This extension can be installed for Python >=3.7 using *pip*

.. bash::

    $ pip3 install fileformats

To also install dependencies required to run converters between select file formats
use the ``converters`` install extra

.. bash::

    $ python3 -m pip install fileformats[converters]

which will enable the following syntax for supported conversions

.. python::

    converted = DesiredFormat.convert(original_file)


MIME Types
----------

File-format types can be read/written as MIME type strings. If the the ``iana`` attribute
is present in the type class, it should correspond to a formally recognised MIME type
by the `Internet Assigned Numbering Authority (IANA) <https://www.iana.org/assignments/media-types/media-types.xhtml>`__, e.g.

.. python::

    from fileformats.core import from_mime

    mime_str = AFormat.mime
    LoadedFormat = from_mime(mime_str)
    assert AFormat is LoadedFormat


Extending
---------



.. .. toctree::
..    :maxdepth: 2
..    :hidden:

..    getting_started
..    data_model
..    processing
..    deployment

.. .. toctree::
..    :maxdepth: 2
..    :caption: Development
..    :hidden:

..    contributing
..    design_analyses
..    adding_formats
..    Alternative storage <alternative_stores.rst>

.. .. toctree::
..    :maxdepth: 2
..    :caption: Reference
..    :hidden:

..    CLI <cli.rst>
..    API <api.rst>


.. _Pydra: http://pydra.readthedocs.io
