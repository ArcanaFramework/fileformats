Adding new types
================

Extensions
----------

*FileFormats* has been designed so that new format classes can be defined to recognise
and handle any weird and whacky file formats in use in a particular domain. These format
classes should be implemented in *FileFormats* extensions, which add sub-packages under
the ``fileformats`` namespace. For example, the
`FileFormats Medimage Extension <https://github.com/ArcanaFramework/fileformats-medimage>`__
implements a range of file formats used in medical imaging research under the
``fileformats.medimage`` package. The
`FileFormats extension template <https://github.com/ArcanaFramework/fileformats-medimage>`__
can be used to quickly create new extensions packages in which to add support for domain-specific
file-types.
