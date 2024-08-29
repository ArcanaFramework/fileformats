Typing
======

As formats are represented by classes, *FileFormats* provides a way to specify finer-grain
type annotations for Python functions and workflows. To these ends, FileFormats also provides a
number of special datatype classes that can be used interchangeably with file formats,
and the ability to augment fileformat types to classify the data contained within them.

Classifiers
-----------

Some FileFormats classes use the ``[]`` class operator to classify the type of data
contained within the file, referred to as "classifiers". For example, a zip file
containing a PNG image, the type can be specified as

.. code-block:: python

    >>> from fileformats.application import Zip
    >>> from fileformats.image import Png, Jpeg

    >>> zip_file = Zip.convert(Png("/path/to/an-image.png"))
    >>> fspath = str(zip_file)
    >>> fspath
    "/path/to/an-image.zip"
    >>> Zip[Png].matches(fspath)
    True
    >>> Zip[Jpeg].matches(fspath)
    False

The types of classes that can be used to classify varies from type to type. For archive
types like :class:`.Zip`, :class:`.Gzip`, take another file format type, others specific
classifier types. Some classifiable types can take multiple classifiers, whereas others can
take one, and the the multiple classifiers can either be ordered or not. In the case of
:class:`.MedicalImage` subclasses, unordered, multiple classifiers based on the
`radlex radiology lexicon <https://radlex.org/>`__ are used to specify the contents of
images

.. code-block:: python

    from fileformats.medimage import NiftiGz, T1Weighted, Brain

    def brain_extraction(image: NiftiGz[T1Weighted, Brain]) -> NiftiGz[Brain, Mask]:
        ...

.. note::
    At the time of writing, only a subset of the RadLex lexicon has been implemented.
    It is being expanded as needed.

When classified types are converted into MIME-like strings, the classifiers are prepended to
the type name with a '+' separator, e.g.


.. code-block:: python

    to_mime(Zip[Png]) == "image/png+zip"


If there are multiple classifiers, then they are arranged in alphabetic order (unless
they are ordered) and separated by a '.' preceding the '+' separator

.. code-block:: python

    to_mime(NiftiGz[T1Weighted, Brain]) == "medimage/brain.t1-weighted+nifti-gz"

Typically the classifier types need to belong to the same registry as the main type, except
in special cases such as :class:`.application.Zip` and :class:`.application.Gzip`, which can be classified by any
file format type. Other special classified types are the :class:`.generic.DirectoryOf`
and :class:`.generic.SetOf` collection types. These can be used to specify that a
"file format" contains a collection of file formats within a directory or independent
files, respectively.

.. code-block:: python

    from fileformats.image import Jpeg, Png
    from fileformats.generic import DirectoryOf, SetOf

    def list_pngs(directory: DirectoryOf[Jpeg]) -> SetOf[Png]:
        return SetOf[Png](Png.convert(j) for j in directory.contents)


Fields
------

There are some use cases where input data can contain a mix of file-based and field data.
Therefore, while not file formats, for convenience *FileFormats* also provides
some field datatypes that can be used interchangeably with file format types for some
use cases, particularly MIME type.

* :class:`.field.Integer`
* :class:`.field.Decimal`
* :class:`.field.Boolean`
* :class:`.field.Text`
* :class:`.field.Array`

A common feature they share is the ability to convert them to/from mime-like (see :ref:`Informal ("MIME-like")`)
strings, e.g. ``to_mime(Integer) == "field/integer"``.


The can be converted to and from their corresponding "primitive types", i.e. ``int``,
``float``, ``bool``, ``str`` and ``list``, either by the object inits

.. code-block:: python

    >>> from fileformats.field import Integer
    >>> my_integer = Integer(1)
    >>> int(my_integer)
    1

or the :meth:`.Field.to_primitive` and :meth:`.Field.from_primitive` methods


.. code-block:: python

    >>> from fileformats.field import Field
    >>> field = Field.from_primitive(1)
    >>> repr(field)
    Integer(1)
    >>> field.to_primitive()
    1


The items contained within an :class:`.Array` class can be specified using the square
brackets operator

.. code-block:: python

    from fileformats.field import Array, Integer, Text, Boolean

    def my_func(int_array: Array[Integer], text_array: Array[Text]) -> Array[Boolean]:
        ...

This will validate the type of data contained within can be converted into the specified
item type

.. code-block:: python

    from fileformats.field import Array, Integer

    int_array = Array[Integer]([1, 2, 3])  # PASSES
    bad_int_array = Array[Integer]([1, 2, 3.5])  # FAILS!


Subclass hooks
--------------

Classified types implement the :meth:`.WithClassifiers.__subclasshook__` method, to control
the behaviour of the :func:`isinstance` and :func:`issubclass` functions when they are
passed as arguments. The unclassified type is always considered to be the superclass of
its classified types

.. code-block:: python

    from fileformats.application import Zip
    from fileformats.image import Png

    assert issubclass(Zip[Png], Zip)
    assert isinstance(Zip[Png]("/path/to/zip.zip"), Zip)

Similarly, for types with multiple unordered classifiers, a type with a subset of the
classifiers of another type is considered to be its superclass

.. code-block:: python

    from fileformats.medimage import NiftiGz, T1Weighted, Brain

    assert issubclass(NiftiGz[T1Weighted, Brain], NiftiGz[T1Weighted])

This is also the case if the classifiers of the  are subclasses of the classifiers
in the subset

.. code-block:: python

    from fileformats.medimage import NiftiGz, T1Weighted, Brain, Mri

    assert issubclass(T1Weighted, Mri)
    assert issubclass(NiftiGz[T1Weighted, Brain], NiftiGz[Mri])

or if the classified type itself is a subclass

.. code-block:: python

    from fileformats.medimage import NiftiGz, NiftiGzX, T1Weighted, Brain, Mri

    assert issubclass(NiftiGzX, NiftiGz)
    assert issubclass(NiftiGzX[T1Weighted, Brain], NiftiGz[T1Weighted, Brain])

For ordered classifiers, the classifiers must be in the same order to be considered
a subclass

.. code-block:: python

    from fileformats.testing import R, A, B, C, E

    assert issubclass(E, C)
    assert issubclass(R[A, B, E], R[A, B, C])
