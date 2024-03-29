
Data Workflows
==============

*FileFormats* is primarily designed for the typing of data workflows to ensure
that data is transferred between workflow nodes in compatible formats. See Pydra_
and Fastr_ for examples of compatible workflow engines.


Base features
~~~~~~~~~~~~~

Base features are available for all types within *FileFormats* and its extension
packages using the base install. They are designed to be broadly available for a large
range of types and very light-weight in terms of external dependencies.


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
arguments to the `DirectoryContaining[]` method,
e.g.

.. code-block:: python

    from fileformats.generic import Directory
    from fileformats.image import Png
    from fileformats.text import Csv

    def my_task(image_dir: DirectoryContaining[Png]) -> Csv:
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

However, file-formats that consist of multiple files (common in scientific
data) will typically define separate required properties for each file. For example, the
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

In the case of file formats with "adjacent" files that share the same file-name stem,
i.e. same file path and name minus the file extension (such as Analyze_), you only need
to provide one the primary path and the header will be automatically detected and added
to the file-set

.. code-block:: python

    >>> from fileformats.medimage import Analyze
    >>> analyze_file = Analyze("/path/to/neuroimage.img")
    >>> analyze_file.fspaths
    {"/path/to/neuroimage.hdr", "/path/to/neuroimage.img"}

This is very useful when reading the output path of a workflow where only primary path
is returned and associated files also need to be saved to an output directory. To copy
all files/directories in a format you can use the ``FileSet.copy()`` method

.. code-block:: python

    >>> analyze_file_copy = analyze_file.copy(dest_dir="/path/to/destination", stem="new-stem")
    >>> analyze_file_copy.fspaths
    {"/path/to/destination/new-stem.hdr", "/path/to/destination/new-stem.img"}

Going in the other direction from a format class to a workflow/task input, the transformation
of the format object to a path-like string is handled implicitly through the
implementation of the ``__str__`` and ``__fspath__`` magic methods. This means
that format objects can be used in place of the path objects themselves, e.g.

.. code-block:: python

    import subprocess
    from fileformats.text import Plain
    text_file = Plain("/path/to/text-file.txt")

    with open(text_file) as f:
        contents = f.read()

    subprocess.run(f"cp {text_file} /path/to/destination", shell=True)

Noting that it is only the "primary" path as returned by the ``fspath`` property that
is rendered.


Extras
~~~~~~

In addition to the basic features of validation and path handling, it is possible to
implement methods to interact with the data of file format objects via "extras hooks".
Such features are added to selected
format classes on a needs basis (pull requests welcome 😊, see :ref:`Developer Guide`),
so are by no means comprehensive, and **are very much provided "as-is"**.

Since these features, typically rely on a range of external libraries, the dependencies
are kept separate and only installed if the ``[extended]`` install option is used
(i.e. ``python3 -m pip install filformats[extended]``).


Metadata
--------

If there has been an extras overload registered for the ``read_metadata`` method,
then metadata associated with the fileset can be accessed via the ``metadata`` property,
e.g.

.. code-block:: python

    >>> dicom.metadata["SeriesDescription"]
    "localizer"


Load/saving data
----------------

Several classes in the base fileformats package implement ``load`` and ``save`` methods.
An advantage of implementing them  in the format class is that objects instantiated from
them can then be duck-typed in calling functions/methods. For example, both ``Yaml`` and
``Json`` formats (both inherit from the ``DataSerialization`` type) implement the
``load`` method, which returns a dictionary

.. code-block:: python

    from fileformats.application import DataSerialization

    def read_json_or_yaml_to_dict(serialized: DataSerialization):
        return serialized.load()

Also, when providing the the ``WithSeparateHeader`` and ``WithSideCars`` mixin classes will

Conversion
----------

Several conversion methods are available between equivalent file-formats in the standard
classes. For example, archive types such as ``Zip`` can be converted into and generic
file/directories using the ``convert`` classmethod of the target format to convert to

.. code-block:: python

    from fileformats.application import Zip
    from fileformats.generic import Directory

    zip_file = Zip.convert(Directory("/path/to/a/directory"))
    extracted = Directory.convert(zip_file)
    copied = extracted.copy_to("/path/to/output")

The converters are implemented in the Pydra_ dataflow framework, and can be linked into
wider Pydra_ workflows by accessing the underlying converter task with the ``get_converter``
classmethod

.. code-block:: python

    import pydra
    from pydra.tasks.mypackage import MyTask
    from fileformats.image import Gif, Png

    wf = pydra.Workflow(name="a_workflow", input_spec=["in_gif"])
    wf.add(
        Png.get_converter(Gif, name="gif2png", in_file=wf.lzin.in_gif)
    )
    wf.add(
        MyTask(
            name="my_task",
            in_file=wf.gif2png.lzout.out_file,
        )
    )
    ...


.. _Pydra: https://pydra.readthedocs.io
.. _Analyze: https://en.wikipedia.org/wiki/Analyze_(imaging_software)
.. _Fastr: https://gitlab.com/radiology/infrastructure/fastr
