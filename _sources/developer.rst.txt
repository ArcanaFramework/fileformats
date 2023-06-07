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

When designing an extension packages, try to keep any external dependencies to a bare
minimum in the base installation, and add them into the ``[extended]`` optional
dependencies. When importing extended dependencies in a module, enclose them in
a try-except statement that catches ImportErrors and sets the module to a
``MissingExtendedDependency`` instead, e.g.

.. code-block:: python

    from fileformats.core import MissingExtendedDependency
    try:
        import external_package
    except ImportError:
        external_package = MissingExtendedDependency("external_package", __name__)

This will raise an informative error message, if a user attempts to access this the
external package.

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


Similar to ``WithSeparateHeader``, ``WithSideCars`` can be used to define a format that
contains some metadata within the main file, and additional metadata in a separate
"side-car" file. It can be used the same as ``WithSeparateHeader``, however, the
type of the primary file that reads the metadata from the binary file with ``load_metadata``
must also be defined in ``primary_type``

.. code-block:: python

    from fileformats.generic import File
    from fileformats.core.mixin import WithSideCars
    from fileformats.serialization import Json

    class FormatWithoutSideCar(File):

         binary = True

        def load_metadata(self):
           ... load metadata in binary...


    class FormatWithSideCars(WithSideCars, File):
        ext = ".fws"
        primary_type = FormatWithoutSideCar
        side_car_types = (Json,)


.. warning::

   Mixin classes in the ``fileformats.core.mixin`` package must come first in the
   method resolution order of the types bases, so that they can override methods in
   ``FileSet`` if need be.


Custom format patterns
----------------------

While the standard mixin classes should cover 90% of all formats, in the wild-west of
scientific data formats you might need to write custom validators using the
``@fileformats.core.mark.required`` and ``@fileformats.core.mark.check`` decorators.

Take for example the `GIS shapefile structure <https://www.earthdatascience.org/courses/earth-analytics/spatial-data-r/shapefile-structure/>`_,
it is a file-set consisting of 3 to 6 files differentiated by their extensions. To
implement this class we use the ``required`` decorator. We inherit from the ``WithAdjacentFiles``
mixin so that neighbouring files (i.e. files with the same stem but different extension)
are included when the class is instantiated with just the primary ".shp" file.

.. code-block:: python

    from fileformats.generic import File
    from fileformats.serialization import Xml
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

        @mark.required
        @property
        def index_file(self):
            return GisShapeIndex(self.select_by_ext(GisShapeIndex))

        @mark.required
        @property
        def features_file(self):
            return GisShapeFeatures(self.select_by_ext(GisShapeFeatures))

        @mark.required
        @property
        def project_file(self):
            return WellKnownText(self.select_by_ext(WellKnownText), allow_none=True)

        @mark.required
        @property
        def spatial_index_n_file(self):
            return GisShapeSpatialIndexN(
               self.select_by_ext(GisShapeSpatialIndexN), allow_none=True
            )

        @mark.required
        @property
        def spatial_index_n_file(self):
            return GisShapeSpatialIndexB(
               self.select_by_ext(GisShapeSpatialIndexB), allow_none=True
            )

        @mark.required
        @property
        def geospatial_metadata_file(self):
            return GisShapeGeoSpatialMetadata(
               self.select_by_ext(GisShapeGeoSpatialMetadata), allow_none=True
            )

By marking the properties as required, means that they need to be able to return a
value without raising a ``FormatsMismatchError`` for the class to be initiated. Required
properties, that appear in ``fspaths`` attribute of the object are considered to be
"required paths", and are copied along side the main path in the ``copy_to`` method.

After the required properties have been deeper checks can be by using the ``check``
decorator. Take the ``fileformats.image.Tiff`` class

.. code-block:: python


    class Tiff(RasterImage):

       ext = ".tiff"
       iana_mime = "image/tiff"

       magic_number_le = "49492A00"
       magic_number_be = "4D4D002A"

       @mark.check
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

The ``Tiff`` format class needs to check two different magic numbers, one for big endian
files and another one for little endian files. Therefore we can't just use the
``WithMagicNumber`` mixin and have to roll our own, ``endianness`` is decorated with
``fileformats.core.mark.check``.


Converters
----------

Converters between two equivalent formats are defined using Pydra_ dataflow engine
`tasks <https://pydra.readthedocs.io/en/latest/components.html>`_. There are two types
of Pydra_ tasks, function tasks, Python functions decorated by ``@pydra.mark.task``, and
shell-command tasks, which wrap command-line tools in Python classes. To register a
Pydra_ task as a converter between two file formats it needs to be decorated with the
``@fileformats.core.mark.converter`` decorator.

Pydra uses type annotations to define the input and outputs of the tasks. It there is
a input to the task named ``in_file``, and either a single anonymous output or an output
named ``out_file``, and both are format classes, then no arguments need to be passed
to the converter decorator and the conversion source and target formats are determined
automatically. For example,

.. code-block:: python

    from pathlib import Path
    import tempfile
    import pydra.mark
    import fileformats.core.mark
    from .mypackage import MyFormat, MyOtherFormat


    @fileformats.core.mark.converter
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
    from fileformats.core import mark
    from .raster import RasterImage, Bitmap, Gif, Jpeg, Png, Tiff


    @mark.converter(target_format=Bitmap, output_format=Bitmap)
    @mark.converter(target_format=Gif, output_format=Gif)
    @mark.converter(target_format=Jpeg, output_format=Jpeg)
    @mark.converter(target_format=Png, output_format=Png)
    @mark.converter(target_format=Tiff, output_format=Tiff)
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

    @mark.converter(source_format=MedicalImage, target_format=Analyze, out_ext=Analyze.ext)
    @mark.converter(
        source_format=MedicalImage, target_format=MrtrixImage, out_ext=MrtrixImage.ext
    )
    @mark.converter(
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


.. note::
    If the converters aren't imported successfully, then you will receive a
    ``FormatConversionError`` error saying there are no converters between FormatA and
    FormatB.


.. _`IANA Media Types`: https://www.iana_mime.org/assignments/media-types/media-types.xhtml
.. _Pydra: https://pydra.readthedocs.io
