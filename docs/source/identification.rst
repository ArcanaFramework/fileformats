Format Identification
=====================

In addition to simply importing and using a format class in your Python code, format classes
can be loaded from their ``MIME type`` (see `IANA Media Types`_), or detected from the
file-system objects.


Detecting formats
-----------------

While not a primary design goal of the *FileFormats* library, it is
possible to detect the formats that match a given set of files using the ``find_matching``
function. Note that it isn't always possible to uniquely identify a single format, since
there may be several matching formats for, non-descript binary file formats that use the
".dat" extension for example.

.. code-block::

    >>> from fileformats.core import find_matching
    >>> find_matching("/path/to/word.doc")
    [<class 'fileformats.document.Msword'>]

Note that the installation of additional sub-packages may cause detection code to
break if your code doesn't the potential of new formats being added with overlapping
cases where they will both match a given file set. If you are only interested in
formats covered in the main fileformats package then you should use the ``standard_only``
flag

.. code-block::

    >>> from fileformats.core import find_matching
    >>> find_matching("/path/to/data.dat", standard_only=True)
    [<class 'fileformats.numeric.DataFile'>]


MIME Types
----------

Namespaces in the ``fileformats`` package are named after MIME type registries
as defined by the Internet Assigned Numbering Authority (IANA) (see `IANA Media Types`_).
The main difference is that there is no "application" registry, which acts as a
catch-all for any type that doesn't have a formal specification. Instead, types that
fall under the "application" registry are grouped by the types of data that they
store, e.g. ``fileformats.archive`` for (typically compressed) archives such as
zip, bzip, gzip, etc..., ``fileformats.document`` for PDFs, word docs,
``fileformats.serialization`` for JSON, YAML and XML, etc...

Format class can be converted to and from MIME type strings using the ``to_mime`` and
``from_mime`` functions. If the the ``iana_mime`` attribute
is present in the type class, it should correspond to a formally recognised MIME type
by the , e.g.

.. code-block:: python

    from fileformats.core import to_mime, from_mime
    from fileformats.image import Png

    Loaded = from_mime("image/png")
    assert Loaded is Png
    assert to_mime(Loaded) == "image/png"

If the format class doesn't define an ``iana_mime`` attribute (i.e. in the actual class,
not including ``iana_mime`` attributes defined in base classes), it will be assigned an informal
MIME-type of "application/x-<transformed-class-name>", where *transformed-class-name*
is the name of the format class converted from "PascalCase" to "kebab-case", with the
first underscore encountered in a class name converted to a "+" and subsequent underscores
converted to ".", e.g.

.. code-block::

    >>> Nifti_Gzip_Bids.mime
    "application/x-nifti+gzip.bids"

Note that if there are two file-formats with the same class name in different sub-packages
then the ``iana_mime`` attribute will need to be set on at least one of them otherwise an
error will be raised they are loaded from a MIME type.

.. warning::
    Note that the installation of additional sub-packages may cause detection code to
    break if your code doesn't the potential of new formats being added with the same
    class name. You may prefer to use "MIME-like" type strings in that case if possible.


MIME-like types
---------------

To avoid the issue with format classes in separate namespaces mapping onto the same
IANA-style MIME type, and for additional clarity (i.e. not drowning in a sea of
"application/x-\*" types), it can be preferable in some use cases not to worry with
closely matching the MIME-type specification for non-standard formats and just use the
file-formats namespace inplace of the generic "application/x-" prefix. This can be done
by setting ``iana=False`` in the ``to_mime`` function, e.g.

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


.. _`IANA Media Types`: https://www.iana_mime.org/assignments/media-types/media-types.xhtml
