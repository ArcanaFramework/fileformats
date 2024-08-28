Fields
======

While not strictly file formats, there are some use cases where input data can contain a
mix of file-based and field data. Therefore, for convenience *FileFormats* also provides
some field datatypes that can be used interchangeably with file format types in some
use cases.

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
