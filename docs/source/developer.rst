Developer Guide
===============

*FileFormats* has been designed so that file-formats specified by standard features,
such as file extension and magic number can be implemented in a few lines, while
still being flexible enough handle any weird whacky file formats used in obscure domains.


Extension packages
------------------

Format classes not covered by `IANA Media Types`_, should be implemented in a separate
*FileFormats* extension packages. Extension packages can be quickly created from the
FileFormats extension template, `<https://github.com/ArcanaFramework/fileformats-medimage>`_.


Extension packages add a new format namespace under the ``fileformats`` namespace package.
For example, the `FileFormats Medimage Extension <https://github.com/ArcanaFramework/fileformats-medimage>`__
implements a range of file formats used in medical imaging research under the
``fileformats.medimage`` namespace.


Basic formats
-------------

In the simplest case of a file format identified by its extension alone, you only need
to inherit from the ``fileformats.generic.File`` class and set the ``ext`` attr, e.g

.. code-block:: python

    from fileformats.generic import File

    class MyFileFormat(File):
        ext = ".my"


Likewise if the format you are defining is a directory containing one or more files of
a given type you can just inherit from the ``fileformats.generic.Directory`` class and
set the ``content_types`` attributes

.. code-block:: python

    from fileformats.generic import Directory
    from fileformats.text import Markdown, Html


    class MyDirFormat(File):
        content_types = (Markdown, Html)


Standard mixins
---------------

If the format is a binary file with a magic number (identifying byte string at start of
file), you can use the ``fileformats.core.mixin.WithMagicNumber`` mixin. For files with
magic numbers you will also need to set the ``binary`` attr to True.

.. code-block:: python

    from fileformats.generic import File
    from fileformats.core.mixin import WithMagicNumber


    class MyBinaryFormat1(WithMagicNumber, File):
        ext = ".myb1"
        binary = True
        magic_number = "98E3F12200AA"  # Unicode strings are interpreted as hex


    class MyBinaryFormat2(WithMagicNumber, File):
        ext = ".myb2"
        binary = True
        magic_number = b"MYB2"  # Byte strings are not converted


Formats will contain metadata in a separate header file can be defined using
the ``WithSeparateHeader`` mixin.

.. code-block:: python

   from fileformats.generic import File
   from fileformats.core.mixin import WithSeparateHeader


    class MyHeaderFormat(File):
        ext = ".hdr"

        def load(self):
            return dict(ln.split(":") for ln in self.contents.splitlines())

    class MyFormatWithHeader(WithSeparateHeader, File):
        ext = ".myh"
        header_type = MyHeaderFormat


The header file can be accessed from an instantiated file object via the ``header``
property. If the header format implements the ``load`` method, then it is assumed to
return a dictionary containing metadata for the file-set.

.. code-block:: python

    >>> my_file = MyFormatWithHeader("/path/to/a/file.myh")
    >>> my_file.header
    MyHeaderFormat(fspaths={"/path/to/a/file.hdr"})
    >>> my_file.metadata["experiment-id"]  # load experiment ID from header file
    '0001'


Similar to ``WithSeparateHeader``, ``WithSideCar`` can be used to define a format that
contains some metadata within the main file, and additional metadata in a separate
"side-car" file. It can be used the same as ``WithSeparateHeader``, however, the
type of the primary file that reads the metadata from the binary file with ``load_metadata``
must also be defined in ``primary_type``

.. code-block:: python

    from fileformats.generic import File
    from fileformats.core.mixin import WithSideCar
    from fileformats.serialization import Json

    class FormatWithoutSideCar(File):

         binary = True

        def load_metadata(self):
           ... load metadata in binary...


    class FormatWithSideCar(WithSideCar, File):
        ext = ".fws"
        primary_type = FormatWithoutSideCar
        side_car_type = Json


.. warning::

   Mixin classes in the ``fileformats.core.mixin`` package must come first in the
   method resolution order of the types bases, so that they can override methods in
   ``FileSet`` if need be.

Custom format patterns
----------------------

.. warning::
   UNDER CONSTRUCTION


Converters
----------

.. warning::
   UNDER CONSTRUCTION



.. _`IANA Media Types`: https://www.iana_mime.org/assignments/media-types/media-types.xhtml
