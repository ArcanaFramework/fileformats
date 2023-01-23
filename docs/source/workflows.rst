
Data Workflows
==============

*FileFormats* is primarily designed for the typing of data workflows to ensure
that data is transferred between workflow nodes in compatible formats.

Validation
----------

In the basic case, *FileFormats* can be used for checking the format of files and
directories against known types. There are two layers of checks, ones
performed on the file-system paths alone, which are run when a format class is
initiated, e.g.

.. code-block:: python

    from fileformats.image import Jpeg

    jpeg_file = Jpeg("/path/to/image.jpg")  # Checks path for correct extension
    jpeg_file = Jpeg("/path/to/image.png")  # <-- THIS WILL FAIL as the extension is wrong


The second layer of checks, which typically require reading the file and peeking at its
contents for magic numbers and the like, are explicitly run by the ``validate`` method.

.. code-block:: python

    fspath = "/path/to/fake-image.jpg"

    with open(fspath, "w") as f:
        f.write("this is not a valid JPEG file")

    jpeg_file = Jpeg(fspath)  # Extension checks out ok
    jpeg_file.validate()  # <-- THIS WILL FAIL as the magic number isn't present


Directory are classified by the contents of the files within them, via the ``content_types``
class attribute, e.g.

.. code-block:: python

    from fileformats.generic import File, Directory

    class DicomFile(File):
        ext = ".dcm"

    class Dicom(Directory):
        content_types = (DicomFile,)


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

In addition, to statically defined Directory formats such as the Dicom example above,
dynamic directory types can be created on the fly using the __class_getitem__ method,
e.g.

.. code-block:: python

    from fileformats.generic import Directory
    from fileformats.image import Png
    from fileformats.text import Csv

    def my_task(image_dir: Directory[Png]) -> Csv:
        ... task implementation ...


Path handling
-------------

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

This is very useful when reading the output path of a workflow where only primary path
is returned and associated files also need to be saved to an output directory. To copy
all files/directories in a format you can use the ``copy_to`` method

.. code-block:: python

    >>> analyze_file_copy = analyze_file.copy_to("/path/to/destination", stem="new-stem")
    >>> analyze_file_copy.fspaths
    {"/path/to/destination/new-stem.hdr", "/path/to/destination/new-stem.img"}

Going in the other direction from a format class to a workflow/task input, the transformation
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
