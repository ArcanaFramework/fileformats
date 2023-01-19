Identifying formats
===================

In addition to simply importing and using a format class in your Python code. There are
several ways to load a class corresponding to given file format, either from the
``MIME type`` (see `IANA Media Types`_) or the file-system objects themselves.

MIME Types
----------

Sub-packages in the ``fileformats`` namespace are named after MIME type registries
as defined by the Internet Assigned Numbering Authority (IANA) (see `IANA Media Types`_).
The main difference is that there is no "application" registry, which acts as a
catch-all for any type that doesn't have a formal specification. Instead, types that
fall under the "application" registry are grouped by the types of data that they
store, e.g. ``fileformats.archive`` for (typically compressed) archives such as
zip, bzip, gzip, etc..., ``fileformats.document`` for PDFs, word docs, and
``fileformats.serialization`` for JSON, YAML and XML.

Format class can be converted to and from MIME type strings using the ``to_mime`` and
``from_mime`` functions. If the the ``iana`` attribute
is present in the type class, it should correspond to a formally recognised MIME type
by the , e.g.

.. code-block:: python

    from fileformats.core import to_mime, from_mime
    from fileformats.image import Png

    Loaded = from_mime("image/png")
    assert Loaded is Png
    assert to_mime(Loaded) == "image/png"

If the format class doesn't define an ``iana`` attribute (i.e. in the actual class,
not including ``iana`` attributes defined in base classes), it will be assigned an informal
MIME-type of "application/x-<transformed-class-name>", where *transformed-class-name*
is the name of the format class converted from "PascalCase" to "kebab-case", with the
first underscore encountered in a class name converted to a "+" and subsequent underscores
converted to ".", e.g.

.. code-block::

    >>> Nifti_Gzip_Bids.mime
    "application/x-nifti+gzip.bids"

Note that if there are two file-formats with the same class name in different sub-packages
then the ``iana`` attribute will need to be set on at least one of them otherwise an
error will be raised they are converted either to or from a MIME type.


MIME-like types
---------------

To avoid the issue with format classes in separate sub-packages mapping onto the same
IANA-style MIME type, and for additional clarity (i.e. not drowning in a sea of
"application/x-\*" types), it can be preferable not to worry with closely matching the
MIME-type specification for non-standard formats and just use the file-formats
sub-package inplace of the "application/x-" prefix. This can be done by setting
``iana=False`` in the ``to_mime`` function, e.g.

.. code-block::

    >>> from fileformats.core import to_mime
    >>> from fileformats.archive import Bzip
    >>> to_mime(Yaml, iana=False)
    "archive/bzip"

The ``from_mime`` function will resolve both official-style MIME types and the MIME-like
types, so it is possible to roundtrip from both.

.. code-block:: python

    from fileformats.core import to_mime, from_mime
    from from fileformats.archive import Bzip
    # Using official-style MIME string
    mime_type = to_mime(Bzip, iana=True)
    assert mime_type == "application/x-bzip"
    assert from_mime(mime_type) is Bzip
    # Using MIME-like string
    mimelike_type = to_mime(Bzip, iana=False)
    assert mimelike_type == "archive/bzip"
    assert from_mime(mimelike_type) is Bzip


Detecting formats
-----------------

While not a key consideration in the design of the *FileFormats* library, it is also
possible to detect the formats that match a given set of files. Note that it isn't
envisaged that this is always possible, there may be many non-descript binary files
with the ".dat" extension for example, and the *FileFormats* is designed to go the
other way, i.e. start with a format you want and see whether the file-system objects
match it. However, the ``detect_format`` function is provided to help detect a
from a given file set.

.. warning::
    Note that the installation of additional sub-packages, may cause a detection to
    stop working, if the additional sub-packages add new formats that are ambiguous
    with previously installed format classes.


.. _`IANA Media Types`: https://www.iana.org/assignments/media-types/media-types.xhtml
