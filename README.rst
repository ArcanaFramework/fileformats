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
.. image:: https://github.com/ArcanaFramework/fileformats/actions/workflows/docs.yml/badge.svg
   :target: https://arcanaframework.github.io/fileformats/
   :alt: docs


*Fileformats* provides a library of file-format types implemented as Python classes.
The file-format types are designed to be used in type validation during the construction
of data workflows (e.g. Pydra_, Fastr_), and also provide some basic data handling methods
(e.g. loading data to dictionaries) and conversions between some equivalent types When
the "extended" install option is provided.

File-format types are typically identified by a combination of file extension
and "magic numbers" where applicable, however, unlike many other file-type Python packages,
*FileFormats*, supports multi-file data formats ("file sets") often found in scientific
workflows, e.g. with separate header/data files. *FileFormats* also provides a flexible
framework to add custom identification routines for exotic file formats, e.g.
formats that require inspection of headers to locate data files, directories containing
certain file types, or to peek at metadata fields to define specific sub-types
(e.g. functional MRI DICOM file set).

See the `extension template <https://github.com/ArcanaFramework/fileformats-extension-template>`__
for instructions on how to design *FileFormats* extensions modules to augment the
standard file-types implemented in the main repository with custom domain/vendor-specific
file-format types. Note that *FileFormats* is a new package, and only has limited support
for standard formats at this stage, although the aim is to include all the official
`IANA MIME types` (hopefully by scraping that site if anyone wants to have a go 😊).


Installation
------------

*FileFormats* can be installed for Python >= 3.7 from PyPI with

.. code-block:: bash

    $ python3 -m pip fileformats


Support for converter methods between a few select formats can be installed by
passing the 'extended' install extra, e.g

.. code-block:: bash

    $ python3 -m pip install fileformats[extended]


Examples
--------

Using the ``WithMagicNumber`` mixin class, the ``Png`` format can be defined concisely as

.. code-block:: python

    from fileformats.generic import File
    from fileformats.core.mixin import WithMagicNumber

    class Png(WithMagicNumber, File):
        binary = True
        ext = ".png"
        iana_mime = "image/png"
        magic_number = b".PNG"


Files can then be checked to see whether they are of PNG format by

.. code-block:: python

    png = Png("/path/to/image/file.png")  # Checks the extension and magic number

which will raise a ``FormatMismatchError`` if initialisation or validation fails, or
for a boolean method that checks the validation use ``matches``

.. code-block:: python

    if Png.matches(a_path_to_a_file):
        ... handle case ...


There are a few selected converters between standard file-format types, perhaps most usefully
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
        MyTask(
            name="my_task",
            in_file=wf.json2yaml.lzout.out_file,
        )
    )
    ...

Alternatively, the conversion can be executed outside of a Pydra_ workflow with

.. code-block:: python

    json_file = Json("/path/to/file.json")
    yaml_file = Yaml.convert(json_file)



License
-------

This work is licensed under a
`Creative Commons Attribution 4.0 International License <http://creativecommons.org/licenses/by/4.0/>`_

.. image:: https://i.creativecommons.org/l/by/4.0/88x31.png
  :target: http://creativecommons.org/licenses/by/4.0/
  :alt: Creative Commons Attribution 4.0 International License

.. _Pydra: https://pydra.readthedocs.io
.. _Fastr: https://gitlab.com/radiology/infrastructure/fastr
.. _`IANA MIME types`: https://www.iana_mime.org/assignments/media-types/media-types.xhtml
