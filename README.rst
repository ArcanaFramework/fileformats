FileFormats
===========
.. image:: https://github.com/arcanaframework/fileformats/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/arcanaframework/fileformats/actions/workflows/tests.yml
.. image:: https://codecov.io/gh/arcanaframework/fileformats/branch/main/graph/badge.svg?token=UIS0OGPST7
   :target: https://codecov.io/gh/arcanaframework/fileformats
.. image:: https://img.shields.io/pypi/pyversions/fileformats-core.svg
   :target: https://pypi.python.org/pypi/fileformats-core/
   :alt: Supported Python versions
.. image:: https://img.shields.io/pypi/v/fileformats-core.svg
   :target: https://pypi.python.org/pypi/fileformats-core/
   :alt: Latest Version

Fileformats provides Python classes for representing different file formats
for use in type hinting and input validation in data workflows. Converters between
equivalent formats are also typically written using the `Pydra <https://pydra.readthedocs.io>`__
dataflow engine are also typically provided.

Each sub-package in the ``fileformats`` namespace is installed in a separate PyPI package,
but can be all installed together by installing the ``fileformats`` meta-package.


Quick Installation
------------------

All sub-packages can be installed by installing the ``fileformats`` meta-package::

    $ python3 -m pip fileformats

which will install the ``core``, and standard fileformat namespaces, ``archive``,
``document``, ``image``, ``numeric``, ``text`` sub-packages within the umbrella
``fileformats`` namespace package.

Developer Installation
----------------------

To install each of the namespace sub-packages so that it is editable, you need to
install each sub-package explicitly. This can be done conveniently from the repo root
directory using a shell "for loop", e.g.::

    $ for subpkg in ./src/fileformats-*; do python3 -m pip install -e ${subpkg}'[test,converters]'; done

License
-------

This work is licensed under a
`Creative Commons Attribution 4.0 International License <http://creativecommons.org/licenses/by/4.0/>`_

.. image:: https://i.creativecommons.org/l/by/4.0/88x31.png
  :target: http://creativecommons.org/licenses/by/4.0/
  :alt: Creative Commons Attribution 4.0 International License
