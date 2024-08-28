Public API
==========

Functions
~~~~~~~~~

.. autofunction:: fileformats.core.to_mime

.. autofunction:: fileformats.core.from_mime

.. autofunction:: fileformats.core.find_matching

.. autofunction:: fileformats.core.from_paths


Core
~~~~

.. autoclass:: fileformats.core.FileSet
    :members: mime_type, mime_like, from_mime, strext, unconstrained, possible_exts, metadata, select_metadata, select_by_ext, matching_exts, convert, get_converter, register_converter, all_formats, standard_formats, hash, hash_files, mock, sample, decomposed_fspaths, from_paths, copy, move

.. autoclass:: fileformats.core.Field
    :members: mime_like, from_mime, to_primitive, from_primitive


Generic
~~~~~~~

.. autoclass:: fileformats.generic.FsObject

.. autoclass:: fileformats.generic.File

.. autoclass:: fileformats.generic.Directory

.. autoclass:: fileformats.generic.DirectoryContaining

.. autoclass:: fileformats.generic.SetOf


Field
~~~~~

.. autoclass:: fileformats.field.Text

.. autoclass:: fileformats.field.Integer

.. autoclass:: fileformats.field.Decimal

.. autoclass:: fileformats.field.Boolean

.. autoclass:: fileformats.field.Array


Mixins
~~~~~~

.. autoclass:: fileformats.core.mixin.WithMagicNumber

.. autoclass:: fileformats.core.mixin.WithMagicVersion

.. autoclass:: fileformats.core.mixin.WithAdjacentFiles

.. autoclass:: fileformats.core.mixin.WithSeparateHeader

.. autoclass:: fileformats.core.mixin.WithSideCars

.. autoclass:: fileformats.core.mixin.WithClassifiers
