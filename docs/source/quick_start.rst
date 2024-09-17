Quick start
===========

Validate the format of a file, in this case a JPEG image, by passing the file path(s) to the
corresponding FileFormat, :class:`fileformats.image.Jpeg`,

.. code-block:: python

   >>> from fileformats.image import Jpeg
   >>> jpeg_file = Jpeg("/path/to/an-image.jpeg")  # check exist., file ext. and magic num.
   >>> str(jpeg_file)  # returns the file path
   "/path/to/an-image.jpeg

For JPEG files, this validation will check the file extension and for the JPEG
`magic number <https://en.wikipedia.org/wiki/Magic_number_(programming)>`__
(``0xffd8ffe0``) at the start of the file. If the file doesn't match the format, the
init method will raise a :class:`.FormatMismatchError`.

For a conditional check instead of validation, use the ``matches`` method.

.. code-block:: python

   >>> if Jpeg.matches("/path/to/an-image.jpeg"):
   ...     print("File is a JPEG image")

The created ``FileSet`` object implements ``os.PathLike`` so can used in place of ``str``
or ``pathlib.Path``, e.g. when opening files

.. code-block:: python

   >>> fp = open(jpeg_file, "rb")
   >>> contents = fp.read()

or in string templates, e.g.

.. code-block:: python

   >>> import subprocess
   >>> subprocess.run(f"cp {jpeg_file} new-dest.jpeg", shell=True)

You can use the ``find_matching`` method to detect the format that matches a given file,
or set of files.

.. code-block:: python

   >>> from fileformats.core import find_matching
   >>> find_matching("/path/to/an-image.jpeg")
   [fileformats.image.raster.Jpeg]

And use the ``to_mime`` and ``from_mime`` methods to convert between file formats and their
MIME types.

   >>> mime = to_mime(Jpeg)
   >>> mime
   "image/jpeg"
   >>> from_mime(mime)
   fileformats.image.raster.Jpeg

To copy or move the files in a :class:`.FileSet` to a new directory, use the
``copy`` or ``move`` methods, respectively.

.. code-block:: python

   >>> new_jpeg = jpeg_file.copy(dest_dir="/path/to/destination")
   >>> new_jpeg.fspaths
   {"/path/to/destination/an-image.jpeg"}

The ``copy`` method also supports creating links (both soft and hard) instead of copying the
file (see :ref:`Copy-mode`).

.. code-block:: python

   >>> new_jpeg = jpeg_file.copy(
   ...    dest_dir="/path/on/same/mount", mode="hardlink_or_copy"
   )  # will perform a hardlink
   >>> new_jpeg2 = jpeg_file.copy(
   ...    dest_dir="/path/to/different/mount", mode="hardlink_or_copy"
   )  # will fallback to a copy

To quickly generate a hash of the file set use the :meth:`.FileSet.hash()` method.

.. code-block:: python

   >>> jpeg_file.hash()
   "d41d8cd98f00b204e9800998ecf8427e"

For selected pairs of formats converter methods have been implement that can be used to
convert between equivalent formats, e.g. to convert a JPEG image to a PNG format.

.. code-block:: python

   >>> from fileformats.image import Png
   >>> png_file = Png.convert(jpeg_file)
   >>> repr(png_file)
   Png("/path/to/an-image.png")

For some select formats there are also methods to read metadata, in which case
the metadata can be accessed as a dictionary attribute.

.. code-block:: python

   >>> from fileformats.application import Dicom
   >>> dcm = Dicom("/path/to/dicom-file.dcm")
   >>> dcm.metadata["SeriesDescription"]
   "t1_mprage_sag_p2_iso_1"

.. note::
   Only a small fraction of formats have extra functionality added in the main package.
   Extra functionality is only planned to be implemented as required. See the :ref:`Extras`
   for information on how to implement new file formats, converters and extra functionality.
