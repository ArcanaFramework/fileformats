
Extras
======

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
