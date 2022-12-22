FileFormats
===========
.. .. image:: https://github.com/arcanaframework/arcana-xnat/actions/workflows/tests.yml/badge.svg
..    :target: https://github.com/arcanaframework/arcana-xnat/actions/workflows/tests.yml
.. .. image:: https://codecov.io/gh/arcanaframework/arcana-xnat/branch/main/graph/badge.svg?token=UIS0OGPST7
..    :target: https://codecov.io/gh/arcanaframework/arcana-xnat
.. .. image:: https://readthedocs.org/projects/arcana/badge/?version=latest
..  :target: http://arcana.readthedocs.io/en/latest/?badge=latest
..   :alt: Documentation Status

Fileformats provides Python classes for representing different file formats
for use in type hinting and input validation in data workflows. Converters between
equivalent formats are also typically written using the `Pydra <https://pydra.readthedocs.io>`__
dataflow engine are also typically provided.

This package only provides the core base classes, which define the structure that
extension classes should adhere to.


Quick Installation
------------------

This extension can be installed for Python 3 using *pip*::

    $ pip3 install fileformats-core


License
-------

This work is licensed under a
`Creative Commons Attribution 4.0 International License <http://creativecommons.org/licenses/by/4.0/>`_

.. image:: https://i.creativecommons.org/l/by/4.0/88x31.png
  :target: http://creativecommons.org/licenses/by/4.0/
  :alt: Creative Commons Attribution 4.0 International License
