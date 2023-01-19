MIME Types
==========

The *FileFormats* package is loosely organised around the organisation of MIME types
(see `Internet Assigned Numbering Authority (IANA) media types <https://www.iana.org/assignments/media-types/media-types.xhtml>`__).
However, non-standard types that fall under the "application" catch-all type

File-format types can be read/written as MIME type strings. If the the ``iana`` attribute
is present in the type class, it should correspond to a formally recognised MIME type
by the , e.g.

.. python::

    from fileformats.core import from_mime

    mime_str = AFormat.mime
    LoadedFormat = from_mime(mime_str)
    assert AFormat is LoadedFormat
