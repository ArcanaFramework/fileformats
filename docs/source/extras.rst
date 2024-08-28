
Extras
======

In addition to the basic features of validation and path handling, it is possible to
implement methods to interact with the data of file format objects via "extras hooks".
Such features are added to selected format classes on a needs basis (pull requests
welcome 😊, see :ref:`Developer Guide`), so are by no means comprehensive, and
are provided "as-is".

Since these features typically rely on a range of external libraries, they are kept in
separate *extras* packages (e.g.
`fileformats-extras <https://pypi.org/project/fileformats-extras/>`__,
`fileformats-medimage-extras <https://pypi.org/project/fileformats-medimage-extras/>`__),
which need to be installed separately.


Metadata
--------

If there has been an extras overload registered for the ``read_metadata`` method,
then metadata associated with the fileset can be accessed via the ``metadata`` property,
e.g.

.. code-block:: python

    >>> dicom.metadata["SeriesDescription"]
    "localizer"

Formats the ``WithSeparateHeader`` and ``WithSideCars`` mixin classes will attempt the
side car if a metadata reader is implemented (e.g. JSON) and merge that with any header
information read from the primary file.


Load/saving data
----------------

Several classes in the base fileformats package implement ``load`` and ``save`` methods.
An advantage of implementing them  in the format class is that objects instantiated from
them can then be duck-typed in calling functions/methods. For example, both ``Yaml`` and
``Json`` formats (both inherit from the ``DataSerialization`` type) implement the
``load`` method, which returns a dictionary

.. code-block:: python

    from fileformats.application import DataSerialization  # i.e. JSON or YAML

    def read_serialisation(serialized: DataSerialization) -> dict:
        return serialized.load()
