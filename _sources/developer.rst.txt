Developer Guide
===============

*FileFormats* has been designed so that file-formats specified by standard features,
such as file extension and magic number can be implemented in a few lines, while
still being flexible enough handle any weird whacky file formats used in obscure domains.


Extension packages
------------------

Format classes not covered by `IANA Media Types`_ should be implemented in a separate
*FileFormats* extension packages. New extension packages can be conveniently created from
the FileFormats extension template, `<https://github.com/ArcanaFramework/fileformats-medimage>`_,
including CI/CD workflows.

Extension packages add a new unique format namespace under the ``fileformats`` namespace package.
For example, the `FileFormats Medimage Extension <https://github.com/ArcanaFramework/fileformats-medimage>`__
implements a range of file formats used in medical imaging research under the
``fileformats.medimage`` namespace.

When designing an extension packages, try to keep any external dependencies to an absolute
minimum (ideally just `attrs`). If you would like to implement extra functionality into
your format classes in addition to the core detection/validation, please use an "extra"
hook and implement the method in an "extras" package (i.e. fileformats-<yournamespace>-extras),
see the `extras template <https://github.com/ArcanaFramework/fileformats-extras-template>`__
for further instructions.


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
the :class:`.WithSeparateHeader` mixin.

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


Similar to :class:`.WithSeparateHeader`, :class:`.WithSideCars` can be used to define a format that
contains some metadata within the main file, and additional metadata in a separate
"side-car" file. It can be used the same as :class:`.WithSeparateHeader`, however, the
type of the primary file that reads the metadata from the binary file with ``read_metadata()``
must also be defined in ``primary_type``


.. warning::

   Mixin classes in the ``fileformats.core.mixin`` package must come first in the
   method resolution order of the types bases, so that they can override methods in
   ``FileSet`` if need be.


Custom format patterns
----------------------

While the standard mixin classes should cover the large majority standard formats, in
the wild-west of science data formats you are likely to need to design custom validators
for your format. This is simply done by adding a new property to the class using the
`@property` decorator.

Take for example the `GIS shapefile structure <https://www.earthdatascience.org/courses/earth-analytics/spatial-data-r/shapefile-structure/>`_,
it is a file-set consisting of 3 to 6 files differentiated by their extensions. To
implement this class we use the ``@property`` decorator. We inherit from the :class:`.WithAdjacentFiles`
mixin so that neighbouring files (i.e. files with the same stem but different extension)
are included when the class is instantiated with just the primary ".shp" file.

.. code-block:: python

    from fileformats.generic import File
    from fileformats.application import Xml
    from fileformats.mixin import WithAdjacentFiles
    from fileformats.core import mark

    class GisShapeIndex(File):
        "the file that indexes the geometry."
        ext = ".shx"


    class GisShapeFeatures(File):
        "the file that stores feature attributes in a tabular format"
        ext = ".dbf"


    class WellKnownText(File):
        """the file that contains information on projection format including the
        coordinate system and projection information. It is a plain text file
        describing the projection using well-known text (WKT) format."""
        ext = ".prj"


    class GisShapeSpatialIndexN(File):
        "the files that are a spatial index of the features."
        ext = ".shn"


    class GisShapeSpatialIndexB(File):
        "the files that are a spatial index of the features."
        ext = ".shb"


    class GisShapeGeoSpatialMetadata(Xml):
        "the file that is the geospatial metadata in XML format"
        ext = ".shp.xml"


    class GisShape(WithAdjacentFiles, File):

        ext = ".shp"  # the main file that will be mapped to fspath

        @property
        def index_file(self):
            return GisShapeIndex(self.select_by_ext(GisShapeIndex))

        @property
        def features_file(self):
            return GisShapeFeatures(self.select_by_ext(GisShapeFeatures))

        @property
        def project_file(self):
            return WellKnownText(self.select_by_ext(WellKnownText), allow_none=True)

        @property
        def spatial_index_n_file(self):
            return GisShapeSpatialIndexN(
               self.select_by_ext(GisShapeSpatialIndexN), allow_none=True
            )

        @property
        def spatial_index_n_file(self):
            return GisShapeSpatialIndexB(
               self.select_by_ext(GisShapeSpatialIndexB), allow_none=True
            )

        @property
        def geospatial_metadata_file(self):
            return GisShapeGeoSpatialMetadata(
               self.select_by_ext(GisShapeGeoSpatialMetadata), allow_none=True
            )

Properties that appear in ``fspaths`` attribute of the object are considered to be
"required paths", and are copied along side the main path in the ``copy_to`` method
even when the ``trim`` argument is set to True.

After the required properties have been deeper checks can be by using the ``check``
decorator. Take the :class:`fileformats.image.Tiff` class

.. code-block:: python


    class Tiff(RasterImage):

       ext = ".tiff"
       iana_mime = "image/tiff"

       magic_number_le = "49492A00"
       magic_number_be = "4D4D002A"

       @property
       def endianness(self):
          read_magic = self.read_contents(len(self.magic_number_le) // 2)
          if read_magic == bytes.fromhex(self.magic_number_le):
                endianness = "little"
          elif read_magic == bytes.fromhex(self.magic_number_be):
                endianness = "big"
          else:
                read_magic_str = bytes.hex(read_magic)
                raise FormatMismatchError(
                   f"Magic number of file '{read_magic_str}' doesn't match either the "
                   f"little-endian '{self.magic_number_le}' and big-endian "
                   f"'{self.magic_number_be}'"
                )
          return endianness

The :class:`.Tiff` format class needs to check two different magic numbers, one for big endian
files and another one for little endian files. Therefore we can't just use the
:class:`.WithMagicNumber` mixin and have to roll our own.


Extra methods
-------------

FileFormats *Extras* enable the creation of hooks in `FileSet` classes using the `@extra`
decorator that can be implemented in separate modules using the `@extra_implementation`
decorator. The "extra methods" typically add additional functionality for accessing and
maninpulating the data within the fileset, i.e. not required for format detection and
validation, and should be implemented in a separate package if they have external
dependencies to keep the main and extension packages dependency free. The
standard place to put these extras-implementations is in the sister "extras" package
named `fileformats-<yournamespace>-extras`, located in the `extras` directory in the
extension package root (see `<https://github.com/ArcanaFramework/fileformats-extension-template>`__
for further instructions). It is possible to implement extra methods in other modules,
however, the extras package associated with formats namespace will be loaded by default
when a hooked method is accessed.

 Use the `@extra` decorator on a method in the to define an extras method,

 .. code-block:: python

    from typing import Self

    class MyFormat(File):

        ext = ".my"

        @extra
        def my_extra_method(self, index: int, scale: float, save_path: Path) -> Self:
            ...

and then reference that method in the extras package using the `@extra_implementation`

.. code-block:: python

    from some_external_package import load_my_format, save_my_format
    from fileformats.core import extra_implementation
    from fileformats.mypackage import MyFormat

    @extra_implementation(MyFormat.my_extra_method)
    def my_extra_method(
        my_format: MyFormat, index: int scale: float, save_path: Path
    ) -> MyFormat:
        data_array = load_my_format(my_format.fspath)
        data_array[:index] *= scale
        save_my_format(save_path, data_array)
        return MyFormat(save_path)

The first argument to the implementation functions is the instance the method
is executed on, and the types of the remaining arguments and return need to match
the hooked method exactly.

It is possible to provide multiple overloads for subclasses of the format that defines
the hook. Like `functools.singledispacth` (which is used under the hood), the type of
the first argument (not the type of the class the method is referenced from in the decorated)
determines which of the overloaded methods is called


.. code-block:: python

    class MyFormatX(MyFormat):
        ext = ".myx"

    @extra_implementation(MyFormat.my_extra_method)
    def my_extra_method(
        my_format: MyFormat, index: int scale: float, save_path: Path
    ) -> MyFormat:
        ...

    @extra_implementation(MyFormat.my_extra_method)
    def my_extra_method(
        my_format: MyFormatX, index: int scale: float, save_path: Path
    ) -> MyFormatX:
        ...


Implementing converters
-----------------------

Converters between two equivalent formats are defined using Pydra_ dataflow engine
`tasks <https://pydra.readthedocs.io/en/latest/components.html>`_. There are two types
of Pydra_ tasks, function tasks, Python functions decorated by ``@pydra.mark.task``, and
shell-command tasks, which wrap command-line tools in Python classes. To register a
Pydra_ task as a converter between two file formats it needs to be decorated with the
``@fileformats.core.converter`` decorator. Like the implementation of extra methods,
converters should be implemented in the sister extras package.

Pydra uses type annotations to define the input and outputs of the tasks. It there is
a input to the task named ``in_file``, and either a single anonymous output or an output
named ``out_file``, and both are format classes, then no arguments need to be passed
to the converter decorator and the conversion source and target formats are determined
automatically. For example,

.. code-block:: python

    from pathlib import Path
    import tempfile
    import pydra.mark
    from fileformats.core import converter
    from .mypackage import MyFormat, MyOtherFormat


    @converter
    @pydra.mark.task
    def convert_my_format(in_file: MyFormat, conversion_argument: int = 2) -> MyOtherFormat:
        data = in_file.load()
        output_path = Path(tempfile.mkdtemp()) / ("out" + MyOtherFormat.ext)
        ... do conversion ...
        return MyOtherFormat.save_new(output_path, data)

defines a converter between ``MyFormat`` and ``MyOtherFormat``, with the converter
argument ``conversion_argument``.

The ``@converter`` decorator registers the class in a class attribute of the target class,
therefore only if module containing the converter methods is imported will the converters
be available. Converter arguments can be passed as keyword-arguments to the
``get_converter`` and ``convert`` methods if required.

Sometimes the source and target formats cannot be automatically determined from the
task signature, and need to be provided as arguments to the ``@converter`` decorator
instead. For example, the converter between raster images using the ``imageio`` package
to do a generic conversion between all image types,

.. code-block:: python

    from pathlib import Path
    import tempfile
    import pydra.mark
    import pydra.engine.specs
    from fileformats.core import converter
    from .raster import RasterImage, Bitmap, Gif, Jpeg, Png, Tiff


    @converter(target_format=Bitmap, output_format=Bitmap)
    @converter(target_format=Gif, output_format=Gif)
    @converter(target_format=Jpeg, output_format=Jpeg)
    @converter(target_format=Png, output_format=Png)
    @converter(target_format=Tiff, output_format=Tiff)
    @pydra.mark.task
    @pydra.mark.annotate({"return": {"out_file": RasterImage}})
    def convert_image(in_file: RasterImage, output_format: type, out_dir: ty.Optional[Path] = None):
        data_array = in_file.load()
        if out_dir is None:
            out_dir = Path(tempfile.mkdtemp())
        output_path = out_dir / (in_file.fspath.stem + output_format.ext)
        return output_format.save_new(output_path, data_array)

In this case because we can write the converter in a generic way that allows us to convert
between any image type supported by ``imageio``, we use the ``RasterImage`` base class
for the input and output format, and explicitly set the ``target_format`` of the output
for each of the support output formats. We also pass ``output_format`` as a keyword argument
from the converter decorator to specify the format we want to convert to.

Note that while the ``source_format`` can be a base class of the format to be converted,
the ``target_format`` can't be, since the subclass my have specific characteristics not
captured by transformation to the base class. However, you can attempt to "cast" a
base class to a sub-class simply by providing the base class as an input, since it will
simply iterate over paths in the base class and attempt to validate them.

.. code-block:: python

    >>> sub_format = SubFormat(BaseFormat.convert(another_format))

Shell commands are marked as converters in the same way as function tasks, and existing
ShellCommandTask classes can be registered by calling the converter method on the ShellCommandTask
directly. If required, you can also map the input and output files to ``in_file`` and
``out_file`` via the converter decorator for any converter task and set appropriate
input fields

.. code-block:: python

    from fileformats.yourpackage import YourFormat, YourOtherFormat
    from pydra.tasks.thirdparty import ThirdPartyShellCmd

    converter(
        source_format=YourFormat,
        target_format=YourOtherFormat,
        in_file=your_file,
        out_file=other_file,
        compression="y",
    )(ThirdPartyShellCmd)

If you need to map any of the converter arguments or perform more complex logic, it is
also possible to decorate a generic function that returns an instantiated Pydra_ task,
such as in the ``mrconvert`` converter in the ``fileformats-medimage`` package.

.. code-block:: python

    @converter(source_format=MedicalImage, target_format=Analyze, out_ext=Analyze.ext)
    @converter(
        source_format=MedicalImage, target_format=MrtrixImage, out_ext=MrtrixImage.ext
    )
    @converter(
        source_format=MedicalImage,
        target_format=MrtrixImageHeader,
        out_ext=MrtrixImageHeader.ext,
    )
    def mrconvert(name, out_ext: str):
        """Initiate an MRConvert task with the output file extension set

        Parameters
        ----------
        name : str
            name of the converter task
        out_ext : str
            extension of the output file, used by MRConvert to determine the desired format

        Returns
        -------
        pydra.ShellCommandTask
            the converter task
        """
        return pydra_mrtrix3_utils.MRConvert(name=name, out_file="out" + out_ext)


Since converter tasks rely on Pydra_, which should be added as an "extended" dependency,
they are not loaded by default. However, if there is a package at
``fileformats.<namespace>.converters``, it will be attempted to be imported and throw
a warning if the import fails, when get_converter is called on a format in that
namespace.


.. warning::
    If the converters aren't imported successfully, then you will receive a
    ``FormatConversionError`` error saying there are no converters between FormatA and
    FormatB.


.. _`IANA Media Types`: https://www.iana_mime.org/assignments/media-types/media-types.xhtml
.. _Pydra: https://pydra.readthedocs.io
