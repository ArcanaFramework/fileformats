MIME Types
==========

In addition to simply importing and using a format class in your Python code, format classes
can be loaded from their `MIME type`_ or `MIME-like` type strings. This can be useful for
dynamically loading formats based on user input, or for identifying the format of a file
based on its MIME type.


Official IANA
-------------

Namespaces in the ``fileformats`` package are largely named after MIME type registries
as defined by the `Internet Assigned Numbering Authority (IANA) <https://www.iana_mime.org/assignments/media-types/media-types.xhtml>`__.
The difference is that there is no "application" registry, which acts as a
bit of a catch-all in the MIME-type specification. Instead, types that
fall under the "application" registry are grouped by the types of data that they
store, e.g. ``fileformats.application`` for (typically compressed) archives such as
zip, bzip, gzip, etc..., ``fileformats.application`` for PDFs, word docs,
``fileformats.application`` for JSON, YAML and XML, etc...

Format class can be converted to and from MIME type strings using the ``to_mime`` and
``from_mime`` functions. If the the ``iana_mime`` attribute
is present in the type class, it should correspond to a formally recognised MIME type
by the , e.g.

.. code-block:: python

    from fileformats.core import to_mime, from_mime
    from fileformats.application import MswordX

    Loaded = from_mime("application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    assert Loaded is MswordX
    assert Loaded.mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

If the format class doesn't define an ``iana_mime`` attribute (i.e. in the actual class,
not including ``iana_mime`` attributes defined in base classes), it will be assigned an informal
MIME-type of "application/x-<transformed-class-name>", where *transformed-class-name*
is the name of the format class converted from "PascalCase" to "kebab-case", with the
single underscores converterd to "." and a double underscores converted to "+" (there
should be only one), e.g.

.. code-block::

    >>> Nifti__Gzip_Json.mime_type
    "application/x-nifti+gzip.json"

Note that if there are two file-formats with the same class name in different sub-packages
then the ``iana_mime`` attribute will need to be set on at least one of them otherwise an
error will be raised when they are loaded from a MIME type.

.. warning::
    Note that the installation of additional sub-packages may cause detection code to
    break if your code doesn't the potential of new formats being added with the same
    class name. Therefore, you may prefer to use "MIME-like" type strings (see below)
    unless IANA compliance is required.


MIME-like
---------

To avoid the issue with format classes in separate namespaces mapping onto the same
IANA-style MIME type, as well as improving readability of the MIME string (i.e. not
drowning in a sea of "application/x-\*" types), it can be preferable in some use cases
not to worry with closely matching the MIME-type specification for non-standard formats
and just use the *FileFormats* namespace inplace of the generic "application/x-" prefix.
This is accessed via the ``mime_like`` class-property.

.. code-block::

    >>> from fileformats.datascience import Hdf5
    >>> from fileformats.medimage import Nifti1
    >>> Hdf5.mime_like
    "datascience/hdf5"
    >>> Nifti1.mime_like
    "medimage/nifti1"

The ``from_mime`` function will resolve both official-style MIME types and the MIME-like
types, so it is possible to roundtrip from both.

.. code-block:: python

    from fileformats.core import to_mime, from_mime
    from from fileformats.medimage import DicomSeries

    # Using official-style MIME string
    mime_type = DicomSeries.mime_type
    assert mime_type == "application/x-dicom-series"
    assert from_mime(mime_type) is DicomSeries

    # Using MIME-like string
    mimelike_type = DicomSeries.mime_like
    assert mimelike_type == "medimage/dicom-series"
    assert from_mime(mimelike_type) is DicomSeries


.. _`MIME type`: https://www.iana_mime.org/assignments/media-types/media-types.xhtml
