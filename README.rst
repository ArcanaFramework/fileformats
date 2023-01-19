FileFormats
===========
.. image:: https://github.com/arcanaframework/fileformats/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/arcanaframework/fileformats/actions/workflows/tests.yml
.. image:: https://codecov.io/gh/arcanaframework/fileformats/branch/main/graph/badge.svg?token=UIS0OGPST7
   :target: https://codecov.io/gh/arcanaframework/fileformats
.. image:: https://img.shields.io/pypi/pyversions/fileformats.svg
   :target: https://pypi.python.org/pypi/fileformats/
   :alt: Supported Python versions
.. image:: https://img.shields.io/pypi/v/fileformats.svg
   :target: https://pypi.python.org/pypi/fileformats/
   :alt: Latest Version
.. image:: https://img.shields.io/github/stars/ArcanaFramework/fileformats.svg
   :alt: GitHub stars
   :target: https://github.com/ArcanaFramework/fileformats
.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat
   :target: https://arcanaframework.github.io/fileformats/
   :alt: Documentation Status


*Fileformats* provides a library of file-format types implemented as Python classes.
The file-format types can be used in type hinting during the construction
of data workflows (e.g. Pydra_), detect and validate the format of files, and move
sets of related files around the file-system together.

Unlike other file-type Python packages, *FileFormats*, supports multi-file
formats, e.g. with separate header/data files, nested directories. It also provides
limited support for loading metadata/data and conversions between some equivalent
types.

File-format types are typically identified by a combination of file extension
and "magic numbers" where applicable. However, *FileFormats* provides a flexible
framework to add custom identification routines for exotic file formats, e.g.
formats that require inspection of headers, directories containing certain files.
See the `extension template <https://github.com/ArcanaFramework/fileformats-extension-template>`__
for instructions on how to add an extension to the standard types.


Installation
------------

All sub-packages can be installed from PyPI with

.. code-block:: bash

    $ python3 -m pip fileformats


Support for converter methods between a few select formats can be installed by
passing the 'converters' install extra, e.g

.. code-block:: bash

    $ python3 -m pip install fileformats[converters]


Examples
--------

Using the ``WithMagic`` mixin class, the ``Png`` format can be defined concisely as

.. code-block:: python

    from fileformats.generic import File
    from fileformats.core.mixin import WithMagic

    class Png(File, WithMagic):
        binary = True
        ext = ".png"
        iana = "image/png"
        magic = b".PNG"


Files can then be checked to see whether they are of PNG format by

.. code-block:: python

    png = Png("/path/to/image/file")
    png.validate()

or more concisely

.. code-block:: python

    if Png.matches("/path/to/image/file"):
        ... do something here


There are a few selected converters between standard file types, perhaps most usefully
between archive types and generic file/directories

.. code-block:: python

    from fileformats.archive import Zip
    from fileformats.generic import Directory

    zip_file = Zip.convert(Directory("/path/to/a/directory"))
    extracted = Directory.convert(zip_file)
    copied = extracted.copy_to("/path/to/output")

The converters are implemented in the Pydra_ dataflow framework, and can be linked into
wider Pydra_ workflows by creating a converter task

.. code-block:: python

    import pydra
    from pydra.tasks.mypackage import MyTask
    from fileformats.serialization import Json, Yaml

    wf = pydra.Workflow(name="a_workflow", input_spec=["in_json"])
    wf.add(
        Yaml.get_converter(Json, name="json2yaml", in_file=wf.lzin.in_json)
    )
    wf.add(
        AnExampleTask(
            name="my_task",
            in_file=wf.json2yaml.lzout.out_file,
        )
    )
    ...

run standalone using the ``Yaml.convert(json_file)`` classmethod.


License
-------

This work is licensed under a
`Creative Commons Attribution 4.0 International License <http://creativecommons.org/licenses/by/4.0/>`_

.. image:: https://i.creativecommons.org/l/by/4.0/88x31.png
  :target: http://creativecommons.org/licenses/by/4.0/
  :alt: Creative Commons Attribution 4.0 International License

.. _Pydra: https://pydra.readthedocs.io
