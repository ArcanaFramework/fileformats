File handling
=============

In addition to validation of format types, *FileFormats* is able to detect related files,
hash them and move them around the file-system as single object.

Paths
-----

Once a file object is initiated you are able to access the properties of the
format class, which for single file formats is typically just the file-system path,
``fspath``.

.. code-block:: python

   >>> from fileformats.image import Jpeg
   >>> jpeg_file = Jpeg("/path/to/image.jpg")
   >>> jpeg_file.fspath
   "/path/to/image.jpg"
   >>> str(jpeg_file)  # returns the path file
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
    >>> str(analyze_file)  # returns the path to the primary file
    "/path/to/neuroimage.img"

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
is returned and associated files also need to be saved to an output directory.

FileSet formats from a format class to a workflow/task input, the transformation
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


Copy
----

To copy all files/directories in a format you can use the ``FileSet.copy()`` method

.. code-block:: python

    >>> new_analyze = analyze_file.copy(dest_dir="/path/to/destination")
    >>> new_analyze.fspaths
    {"/path/to/destination/t1w.hdr", "/path/to/destination/t1w.img"}


Mode
~~~~

The copy method also supports creating links (both soft and hard) instead of copying the
file by passing a value from the :class:`.FileSet.CopyMode` enum to the ``mode`` argument.

.. code-block:: python

    >>> from fileformats.core import FileSet
    >>> new_analyze = analyze_file.copy(
        dest_dir="/path/to/destination", mode=FileSet.CopyMode.hardlink
    )
    >>> new_analyze.fspaths
    {"/path/to/destination/t1w.hdr", "/path/to/destination/t1w.img"}

For some applications you might prefer to create a link instead of creating a duplicate
of the original files, but depending on the mounts/drives that the source files and
destination directories sit on this might not be possible due to limitations of the
file-system, or the source and destination locations being different physical drives
(and therefore can't hardlink). To handle these cases the ``mode`` flag can be set to a
combination of link and copy modes,


.. code-block:: python

    new_analyze = analyze_file.copy(
        dest_dir="/path/to/destination", mode=FileSet.CopyMode.link_or_copy
    )

in which case the copy method will attempt to create a symlink, then if that fails, a
hardlink, and failing that fallback to a copy. The supported modes can also be specified
manually by passing a :class:`.FileSet.CopyMode` flag to the ``supported_modes``
argument, which will be used to mask the requested ``mode``. Note that automatically detected
unsupported modes will be masked out of the ``supported_modes`` before it is applied.

.. code-block:: python

    new_analyze = analyze_file.copy(
        dest_dir="/path/to/destination",
        mode=user_requested,
        supported_modes=FileSet.CopyMode.hardlink_or_copy
    )


Collation
~~~~~~~~~

When working with file formats with multiple files, there is not requirement that the
filepaths are adjacent to each other in the same , for example

.. code-block:: python

    >>> from fileformats.medimage import NiftiX
    >>> niftix = NiftiX(["/a/path/to/a/t1w.nii", "/an/unrelated/path/t1-weighted.json"])

However, some commands expect auxiliary files to be "adjacent" to the primary file, i.e.
in the same directory as the primary with the same file stem. To support this use case,
the :meth:`.FileSet.copy()` can be passed a ``collation`` argument, which takes a
:class:`.FileSet.Collation` enum value.

.. code-block:: python

    >>> new_niftix = niftix.copy(
        dest_dir="/path/to/destination", collation=FileSet.Collation.adjacent
    )
    >>> new_niftix.fspaths
    {"/path/to/destination/t1w.nii", "/path/to/destination/t1w.json"}

To control what the files are collated as, the ``new_stem`` argument can be passed to
the ``copy()`` method.

.. code-block:: python

    >>> new_niftix = niftix.copy(
        dest_dir="/path/to/destination", new_stem="t1-weighted"
    )
    >>> new_niftix.fspaths
    {"/path/to/destination/t1-weighted.nii", "/path/to/destination/t1-weighted.json"}


.. code-block:: python

    >>> new_analyze = analyze_file.copy(dest_dir="/path/to/destination")
    >>> new_analyze.fspaths
    {"/path/to/destination/t1w.hdr", "/path/to/destination/t1w.img"}

If the files just need to be in the same directory, but not necessarily adjacent, the
``collation`` argument can be set to ``FileSet.Collation.siblings``

.. code-block:: python

    >>> new_niftix = niftix.copy(
        dest_dir="/path/to/destination", collation=FileSet.Collation.siblings
    )
    >>> new_niftix.fspaths
    {"/path/to/destination/t1w.nii", "/path/to/destination/t1-weighted.json"}


The collation setting can also be used to decide whether files need to be copied or linked
to a new location. For example, if the files are already adjacent, then they can be simply
left where they are by setting the mode to ``FileSet.CopyMode.any`` flag, which encompasses the
``FileSet.CopyMode.leave`` mode.

.. code-block:: python

    >>> new_niftix = niftix.copy(
        dest_dir="/path/to/destination",
        collation=FileSet.Collation.adjacent,
        mode=FileSet.CopyMode.any
    )

The behaviour of this copy becomes a little complex and will be determined by the
file paths in the ``niftix`` FileSet and the location of the source and destination
directories. For example, if the file paths are already adjacent in the source directory
they will be left where they are. However, if the files are not adjacent, they will be
symlinked to the destination directory, unless the mount that directory is on doesn't
support symlinks, in which case they will be hardlinked, unless the destination directory
is on a different physical drive, in which case they will be copied.


Moving
------

The ``FileSet.move()`` method can be used to move files to a new location. It has same
signature as ``FileSet.move()`` with the exception of the ``mode`` and ``supported_modes``
arguments, which are not relevant for moving files.

.. code-block:: python

    >>> new_analyze = analyze_file.move(
        dest_dir="/path/to/destination", new_stem="t1-weighted"
    )
    >>> new_analyze.fspaths
    {"/path/to/destination/t1-weighted.hdr", "/path/to/destination/t1-weighted.img"}


Hashing
-------

When working with files, particularly in workflows, it is often useful to be able to
hash the contents of the files in the set to check for changes or successful transfers.

There are two methods for doing this conveniently in *FileFormats*:

1. The ``FileSet.hash()`` method will hash the contents of all files in the set and return
   a hash value.
2. The ``FileSet.hash_files()`` method will hash the contents of all files in the set and
   return a dictionary of hashes keyed by the file path.


.. _Analyze: https://en.wikipedia.org/wiki/Analyze_(imaging_software)
