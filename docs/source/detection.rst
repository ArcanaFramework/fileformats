
Detection
=========

*FileFormats* has been designed to detect whether a set of files matches a given
format specification. This can be used either be in the form of validating file types
in workflows or identifying the format in which user input files have been provided.

Validation
----------

In the basic case, *FileFormats* can be used for checking the format of files and
directories against known types. Typically this will involve checking the file extension
and magic number if applicable

.. code-block:: python

    from fileformats.image import Jpeg

    jpeg_file = Jpeg("/path/to/image.jpg")  # PASSES
    Jpeg("/path/to/image.png")  # FAILS!

    fake_fspath = "/path/to/fake-image.jpg"

    with open(fake_fspath, "w") as f:
        f.write("this is not a valid JPEG file")

    Jpeg(fake_fspath)  # FAILS!

To check whether a format matches without attempting to initialise the object use the
:meth:`FileSet.matches()` method


.. code-block:: python

    if Jpeg.matches("/path/to/image.jpg"):
        ...


Directories are classified by the contents of the files within them, via the
``content_types`` class attribute, e.g.

.. code-block:: python

    from fileformats.generic import File, Directory

    class Dicom(WithMagicNumber, File):
        magic_number = b"DICM"
        magic_number_offset = 128

    class  DicomDir(Directory):
        content_types = (Dicom,)


Note that only one file within the directory needs to match the specified content type
for it to be considered a match and additional files will be ignored. For example,
the ``Dicom`` type would be considered valid on the following directory structure
despite the presence of the ``.DS_Store`` directory and the ``catalog.xml`` file.

.. code-block::

    dicom-directory
    ├── .DS_Store
    │   ├── deleted-file1.txt
    │   ├── deleted-file2.txt
    │   └── ...
    ├── 1.dcm
    ├── 2.dcm
    ├── 3.dcm
    ├── ...
    ├── 1024.dcm
    └── catalog.xml

In addition to statically defining `Directory` formats such as the Dicom example above,
dynamic directory types can be created on the fly by providing the content types as
"classifier" arguments to the `DirectoryOf[]` class (see :ref:`Classifiers`),
e.g.

.. code-block:: python

    from fileformats.generic import Directory
    from fileformats.image import Png
    from fileformats.text import Csv

    def my_task(image_dir: DirectoryOf[Png]) -> Csv:
        ... task implementation ...


Identification
--------------

The ``find_matching`` function can be used to list the formats that match a given file

.. code-block::

    >>> from fileformats.core import find_matching
    >>> find_matching(["/path/to/word.doc"])
    [<class 'fileformats.application.Msword'>]

.. warning::
   The installation of extension packages may cause detection code to break if one of
   the newly added formats also matches the file and your code doesn't handle this case.
   If you are only interested in formats covered in the main fileformats package then
   you should use the ``standard_only`` flag

For loosely formats without many constraints, ``find_matching`` may return multiple
formats that are not plausible for the given use case, in which case the ``candidates``
argument can be passed to restrict the possible formats that can be returned

.. code-block::

    >>> from fileformats.datascience import MatFile, RData, Hdf5
    >>> find_matching(["/path/to/text/matrix/file.mat"])
    [fileformats.datascience.data.TextMatrix]
    >>> find_matching(["/path/to/matlab/file.mat"])
    [fileformats.datascience.data.TextMatrix, fileformats.datascience.data.MatFile]
    >>> find_matching(["/path/to/matlab/file.mat"], candidates=[MatFile, RData, Hdf5])
    [fileformats.datascience.data.MatFile]

``from_paths`` can be used to return an initialised object instead of a list of matching
files, however, since you need to be confident that there is only than one possible format
it is advisable to also provide a list of candidate formats

.. code-block::

    >>> from fileformats.core import from_paths
    >>> repr(from_paths(["/path/to/matlab/file.mat"], candidates=[MatFile, RData, Hdf5]))
    fileformats.datascience.data.MatFile({"/path/to/matlab/file.mat"})
