
Detection
=========

*FileFormats* has been designed to detect whether a set of files matches a given
format specification. This can be used either be in the form of validating file types
in workflows or identifying the format in which user input files have been provided.

Validation
----------

In the basic case, *FileFormats* can be used for checking the format of files and
directories against known types. Typically, there are two layers of checks, ones
performed on the file-system paths alone,

.. code-block:: python

    from fileformats.image import Jpeg

    jpeg_file = Jpeg("/path/to/image.jpg")  # PASSES
    jpeg_file = Jpeg("/path/to/image.png")  # FAILS!


The second layer of checks, which typically require reading the file and peeking at its
contents for magic numbers and the like

.. code-block:: python

    fspath = "/path/to/fake-image.jpg"

    with open(fspath, "w") as f:
        f.write("this is not a valid JPEG file")

    jpeg_file = Jpeg(fspath)  # FAILS!


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
arguments to the `DirectoryOf[]` method,
e.g.

.. code-block:: python

    from fileformats.generic import Directory
    from fileformats.image import Png
    from fileformats.text import Csv

    def my_task(image_dir: DirectoryOf[Png]) -> Csv:
        ... task implementation ...

.. _Pydra: https://pydra.readthedocs.io
.. _Fastr: https://gitlab.com/radiology/infrastructure/fastr


Identification
--------------

The ``find_matching`` function can be used to list the formats that match a given file

.. code-block::

    >>> from fileformats.core import find_matching
    >>> find_matching("/path/to/word.doc")
    [<class 'fileformats.application.Msword'>]

.. warning::
   The installation of extension packages may cause detection code to break if one of
   the newly added formats also matches the file and your code doesn't handle this case.
   If you are only interested in formats covered in the main fileformats package then
   you should use the ``standard_only`` flag

Alter
