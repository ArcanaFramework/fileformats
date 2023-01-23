Developer Guide
===============

*FileFormats* has been designed so that file-formats specified by standard features,
such as file extension and magic number can be implemented in a few lines, while
still being flexible enough handle any weird whacky file formats used in obscure domains.


Extension packages
------------------

Format classes not covered by `IANA Media Types`_, should be implemented in a separate
*FileFormats* extension packages. Extension packages can be quickly created from the
`FileFormats extension template <https://github.com/ArcanaFramework/fileformats-medimage>`__.
Extension packages add a new format namespace under the ``fileformats`` namespace package.
For example, the `FileFormats Medimage Extension <https://github.com/ArcanaFramework/fileformats-medimage>`__
implements a range of file formats used in medical imaging research under the
``fileformats.medimage`` namespace.


Defining formats using standard patterns
----------------------------------------

.. warning::
   UNDER CONSTRUCTION


Custom format patterns
----------------------

.. warning::
   UNDER CONSTRUCTION


Converters
----------

.. warning::
   UNDER CONSTRUCTION



.. _`IANA Media Types`: https://www.iana_mime.org/assignments/media-types/media-types.xhtml
